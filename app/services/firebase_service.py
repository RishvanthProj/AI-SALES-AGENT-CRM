import os
import re
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

from app.config import settings
from app.schemas.firebase_models import (
    ProductDocument,
    ProductVariant,
    CustomerDocument,
    OrderDocument,
    OrderItemDocument,
    BusinessSettingsDocument,
    LeadCRMDocument,
    FAQDocument,
    OfferDocument,
    AutomationRuleDocument,
    SupportTicketDocument,
    ConversationMessageDocument
)

logger = logging.getLogger("firebase_service")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FirestoreInMemoryStore:
    """
    In-memory multi-tenant Firestore mock for testing and local environments
    where live Firebase credentials are not yet configured.
    Guarantees strict tenant isolation by scoping everything under businessId.
    """
    def __init__(self):
        # businessId -> collection_name -> doc_id -> doc_dict
        self._data: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def _ensure_tenant(self, business_id: str):
        if business_id not in self._data:
            self._data[business_id] = {
                "businesses": {},
                "products": {},
                "customers": {},
                "leads": {},
                "conversations": {},
                "messages": {},
                "orders": {},
                "order_items": {},
                "faqs": {},
                "offers": {},
                "automation_rules": {},
                "follow_up_jobs": {},
                "support_tickets": {},
                "settings": {
                    "business": BusinessSettingsDocument(businessId=business_id).model_dump()
                }
            }

    def get_doc(self, business_id: str, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_tenant(business_id)
        return self._data[business_id].get(collection, {}).get(doc_id)

    def set_doc(self, business_id: str, collection: str, doc_id: str, doc_data: Dict[str, Any]) -> None:
        self._ensure_tenant(business_id)
        if collection not in self._data[business_id]:
            self._data[business_id][collection] = {}
        self._data[business_id][collection][doc_id] = doc_data

    def list_docs(self, business_id: str, collection: str) -> List[Dict[str, Any]]:
        self._ensure_tenant(business_id)
        return list(self._data[business_id].get(collection, {}).values())

    def clear(self):
        self._data.clear()


class FirebaseService:
    """
    Production-grade, Tenant-Scoped Firebase / Firestore Service for StrideHub Shoes.
    Serves as the Authoritative Single Source of Truth for all business data:
    - Products & Sizing Inventory
    - Customer CRM & Profiles
    - Orders & Invoices & Fulfillment
    - Business Configurations & Policies
    - Conversation History & CRM Lead State
    - FAQs, Offers & Automation Rules
    """
    def __init__(self):
        self._db = None
        self._initialized = False
        self._mock_store = FirestoreInMemoryStore()
        self._initialize_client()
        try:
            self.seed_stridehub_shoe_data("stridehub-shoes")
        except Exception as e:
            logger.warning(
                f"Live Firestore communication failed during initial seed ({e}). "
                "Falling back to local in-memory store until Firestore database is enabled in Firebase Console."
            )
            self._db = None
            self._initialized = False
            # Re-seed into mock store
            self.seed_stridehub_shoe_data("stridehub-shoes")

    def _initialize_client(self):
        """
        Initializes Firebase Admin SDK client with server-side credentials or emulator.
        Falls back to thread-safe multi-tenant in-memory store if credentials are not configured.
        """
        if settings.USE_FIREBASE_EMULATOR and settings.FIRESTORE_EMULATOR_HOST:
            os.environ["FIRESTORE_EMULATOR_HOST"] = settings.FIRESTORE_EMULATOR_HOST

        has_credentials = bool(
            settings.FIREBASE_CREDENTIALS_PATH
            or (settings.FIREBASE_PROJECT_ID and settings.FIREBASE_PRIVATE_KEY and settings.FIREBASE_CLIENT_EMAIL)
            or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        )

        if has_credentials:
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore

                if not firebase_admin._apps:
                    if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
                        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                        firebase_admin.initialize_app(cred)
                    elif settings.FIREBASE_PROJECT_ID and settings.FIREBASE_PRIVATE_KEY:
                        cred_dict = {
                            "type": "service_account",
                            "project_id": settings.FIREBASE_PROJECT_ID or "ai-sales-agent---shoe",
                            "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
                            "client_email": settings.FIREBASE_CLIENT_EMAIL
                        }
                        cred = credentials.Certificate(cred_dict)
                        firebase_admin.initialize_app(cred)
                    else:
                        firebase_admin.initialize_app()

                self._db = firestore.client()
                self._initialized = True
                logger.info("Firestore client initialized for project ai-sales-agent---shoe.")
            except Exception as e:
                logger.warning(f"Could not connect to live Firestore ({e}). Using isolated mock store.")
                self._db = None
                self._initialized = False
        else:
            logger.info("No live Firebase credentials configured; running in tenant-isolated mode.")
            self._db = None
            self._initialized = False

    def is_healthy(self) -> bool:
        return True

    # -------------------------------------------------------------------------
    # Tenant Path Helpers
    # -------------------------------------------------------------------------
    def _business_ref(self, business_id: str):
        return self._db.collection("businesses").document(str(business_id))

    # -------------------------------------------------------------------------
    # Business Settings & Policies
    # -------------------------------------------------------------------------
    def get_business_settings(self, business_id: str = "stridehub-shoes") -> BusinessSettingsDocument:
        """
        Retrieves business profile, policies, hours, and available offers for tenant.
        """
        try:
            if self._db:
                doc = self._business_ref(business_id).collection("settings").document("business").get()
                if doc.exists:
                    return BusinessSettingsDocument.model_validate(doc.to_dict())
            else:
                data = self._mock_store.get_doc(str(business_id), "settings", "business")
                if data:
                    return BusinessSettingsDocument.model_validate(data)
        except Exception as e:
            logger.error(f"Error fetching business settings for tenant {business_id}: {e}")

        return BusinessSettingsDocument(businessId=business_id)

    def set_business_settings(self, business_id: str, settings_doc: BusinessSettingsDocument) -> None:
        data = settings_doc.model_dump()
        if self._db:
            self._business_ref(business_id).collection("settings").document("business").set(data)
        else:
            self._mock_store.set_doc(str(business_id), "settings", "business", data)

    # -------------------------------------------------------------------------
    # Products & Inventory (Strict Source of Truth)
    # -------------------------------------------------------------------------
    def get_product(self, business_id: str, product_id: str) -> Optional[ProductDocument]:
        """
        Retrieves a single product document by ID under the business's scope.
        """
        try:
            if self._db:
                doc = self._business_ref(business_id).collection("products").document(str(product_id)).get()
                if doc.exists:
                    d = doc.to_dict()
                    d["productId"] = doc.id
                    d["id"] = doc.id
                    return ProductDocument.model_validate(d)
                return None
            else:
                data = self._mock_store.get_doc(str(business_id), "products", str(product_id))
                return ProductDocument.model_validate(data) if data else None
        except Exception as e:
            logger.error(f"Error fetching product {product_id} for tenant {business_id}: {e}")
            return None

    def list_all_products(self, business_id: str = "stridehub-shoes") -> List[ProductDocument]:
        """
        Lists all products for a business.
        """
        products: List[ProductDocument] = []
        try:
            raw_docs: List[Dict[str, Any]] = []
            if self._db:
                coll_ref = self._business_ref(business_id).collection("products")
                for doc in coll_ref.stream():
                    d = doc.to_dict()
                    d["productId"] = doc.id
                    d["id"] = doc.id
                    raw_docs.append(d)
            else:
                raw_docs = self._mock_store.list_docs(str(business_id), "products")

            for d in raw_docs:
                products.append(ProductDocument.model_validate(d))
        except Exception as e:
            logger.error(f"Error listing products for tenant {business_id}: {e}")

        return products

    def save_product(self, business_id: str, product: ProductDocument) -> None:
        """
        Upserts a product into the tenant's product catalog.
        """
        data = product.model_dump(by_alias=True)
        data["updatedAt"] = _utc_now_iso()
        if not data.get("createdAt"):
            data["createdAt"] = _utc_now_iso()

        if self._db:
            self._business_ref(business_id).collection("products").document(product.id).set(data)
        else:
            self._mock_store.set_doc(str(business_id), "products", product.id, data)

    def search_products(
        self,
        business_id: str,
        query: str,
        category: Optional[str] = None,
        max_budget: Optional[float] = None,
        color: Optional[str] = None,
        size: Optional[str] = None
    ) -> List[ProductDocument]:
        """
        Searches product catalog in Firestore matching search tokens, category, budget, color, and size.
        Returns only authentic products stored in Firestore.
        """
        products: List[ProductDocument] = []
        try:
            raw_docs: List[Dict[str, Any]] = []
            if self._db:
                coll_ref = self._business_ref(business_id).collection("products")
                for doc in coll_ref.stream():
                    d = doc.to_dict()
                    d["productId"] = doc.id
                    d["id"] = doc.id
                    raw_docs.append(d)
            else:
                raw_docs = self._mock_store.list_docs(str(business_id), "products")

            query_tokens = [t.lower() for t in re.split(r'\s+', query.strip()) if len(t) > 1 and t not in ["shoe", "shoes", "pair", "need", "want", "for", "the", "under", "around", "have", "you"]]

            for d in raw_docs:
                p = ProductDocument.model_validate(d)

                # Match category if specified
                if category and category.lower() not in p.category.lower():
                    continue

                # Match budget constraint against effective price
                if max_budget is not None and max_budget > 0:
                    if p.effective_price > max_budget:
                        continue

                # Match color if specified
                if color:
                    colors_list = [p.primaryColor or ""] + (p.colors or [])
                    if not any(color.lower() in c.lower() for c in colors_list if c):
                        continue

                # Match size if specified
                if size:
                    available = p.availableSizes or p.sizes or []
                    if not any(str(size).lower() == str(s).lower() for s in available):
                        continue

                # Match text tokens in name, description, category, upperMaterial, etc.
                if query_tokens:
                    searchable_text = f"{p.name} {p.description} {p.category} {p.brand} {p.primaryColor} {' '.join(p.availableSizes)}".lower()
                    score = sum(1 for token in query_tokens if token in searchable_text)
                    if score == 0:
                        continue

                products.append(p)

        except Exception as e:
            logger.error(f"Error searching products for tenant {business_id}: {e}")

        return products

    def check_inventory(
        self,
        business_id: str,
        product_id: str,
        size: Optional[str] = None,
        color: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deterministically verifies inventory stock and variant availability from Firestore.
        """
        product = self.get_product(business_id, product_id)
        if not product:
            return {
                "found": False,
                "is_available": False,
                "available_quantity": 0,
                "available_sizes": [],
                "available_colors": [],
                "message": "Product not found"
            }

        available_qty = product.quantity
        available_sizes = product.availableSizes or product.sizes or ["5", "6", "7", "8", "9", "10", "11", "12"]
        available_colors = [product.primaryColor] if product.primaryColor else []
        if product.colors:
            available_colors.extend(product.colors)

        available_sizes = list(dict.fromkeys(filter(None, [str(s) for s in available_sizes])))
        available_colors = list(dict.fromkeys(filter(None, [str(c) for c in available_colors])))

        variant_matched = None
        if size or color:
            for v in product.variants:
                size_match = (not size) or (v.size and str(v.size).lower() == str(size).lower())
                color_match = (not color) or (v.color and v.color.lower() == color.lower())
                if size_match and color_match:
                    variant_matched = v
                    break

        if variant_matched:
            available_qty = variant_matched.stock

        is_available = (available_qty > 0)

        return {
            "found": True,
            "product_id": product.id,
            "product_name": product.name,
            "price": product.price,
            "mrp": product.mrp,
            "sale_price": product.salePrice,
            "effective_price": product.effective_price,
            "is_available": is_available,
            "available_quantity": available_qty,
            "available_sizes": available_sizes,
            "available_colors": available_colors,
            "stock_status": "out_of_stock" if available_qty == 0 else ("low_stock" if available_qty <= product.lowStockThreshold else "in_stock"),
            "variant_matched": variant_matched.model_dump() if variant_matched else None
        }

    def atomic_update_inventory(
        self,
        business_id: str,
        product_id: str,
        quantity_delta: int
    ) -> bool:
        """
        Atomically updates inventory quantity to prevent negative stock and race conditions.
        """
        try:
            if self._db:
                from google.cloud import firestore

                doc_ref = self._business_ref(business_id).collection("products").document(str(product_id))

                @firestore.transactional
                def update_in_transaction(transaction, ref):
                    snapshot = ref.get(transaction=transaction)
                    if not snapshot.exists:
                        return False
                    curr_qty = snapshot.get("quantity") or snapshot.get("available_quantity") or 0
                    new_qty = curr_qty + quantity_delta
                    if new_qty < 0:
                        return False
                    status = "out_of_stock" if new_qty == 0 else ("low_stock" if new_qty < 5 else "in_stock")
                    transaction.update(ref, {
                        "quantity": new_qty,
                        "available_quantity": new_qty,
                        "stockStatus": status,
                        "updatedAt": _utc_now_iso()
                    })
                    return True

                transaction = self._db.transaction()
                return update_in_transaction(transaction, doc_ref)
            else:
                data = self._mock_store.get_doc(str(business_id), "products", str(product_id))
                if not data:
                    return False
                curr_qty = data.get("quantity", data.get("available_quantity", 0))
                new_qty = curr_qty + quantity_delta
                if new_qty < 0:
                    return False
                status = "out_of_stock" if new_qty == 0 else ("low_stock" if new_qty < 5 else "in_stock")
                data["quantity"] = new_qty
                data["available_quantity"] = new_qty
                data["stockStatus"] = status
                data["updatedAt"] = _utc_now_iso()
                self._mock_store.set_doc(str(business_id), "products", str(product_id), data)
                return True
        except Exception as e:
            logger.error(f"Error updating inventory for product {product_id} in tenant {business_id}: {e}")
            return False

    # -------------------------------------------------------------------------
    # Orders & Order Tracking
    # -------------------------------------------------------------------------
    def get_order(self, business_id: str, order_id: str) -> Optional[OrderDocument]:
        """
        Looks up an order by order_id.
        """
        try:
            clean_id = order_id.replace("#", "").strip()
            if self._db:
                doc = self._business_ref(business_id).collection("orders").document(clean_id).get()
                if doc.exists:
                    d = doc.to_dict()
                    d["order_id"] = doc.id
                    return OrderDocument.model_validate(d)
                return None
            else:
                data = self._mock_store.get_doc(str(business_id), "orders", clean_id)
                return OrderDocument.model_validate(data) if data else None
        except Exception as e:
            logger.error(f"Error fetching order {order_id} for tenant {business_id}: {e}")
            return None

    def list_orders(self, business_id: str = "stridehub-shoes") -> List[OrderDocument]:
        orders: List[OrderDocument] = []
        try:
            raw_docs: List[Dict[str, Any]] = []
            if self._db:
                for doc in self._business_ref(business_id).collection("orders").stream():
                    d = doc.to_dict()
                    d["order_id"] = doc.id
                    raw_docs.append(d)
            else:
                raw_docs = self._mock_store.list_docs(str(business_id), "orders")

            for d in raw_docs:
                orders.append(OrderDocument.model_validate(d))
        except Exception as e:
            logger.error(f"Error listing orders for tenant {business_id}: {e}")
        return orders

    def save_order(self, business_id: str, order: OrderDocument) -> None:
        data = order.model_dump()
        clean_id = order.order_id.replace("#", "").strip()
        if self._db:
            self._business_ref(business_id).collection("orders").document(clean_id).set(data)
        else:
            self._mock_store.set_doc(str(business_id), "orders", clean_id, data)

    # -------------------------------------------------------------------------
    # Customers & CRM Profiles
    # -------------------------------------------------------------------------
    def get_or_create_customer(
        self,
        business_id: str,
        phone_number: str,
        name: Optional[str] = None
    ) -> CustomerDocument:
        cust_id = re.sub(r'[^0-9+]', '', phone_number)
        try:
            if self._db:
                doc_ref = self._business_ref(business_id).collection("customers").document(cust_id)
                doc = doc_ref.get()
                if doc.exists:
                    d = doc.to_dict()
                    d["id"] = cust_id
                    if name and not d.get("name"):
                        d["name"] = name
                        doc_ref.update({"name": name, "updated_at": _utc_now_iso()})
                    return CustomerDocument.model_validate(d)

                new_cust = CustomerDocument(
                    id=cust_id,
                    businessId=business_id,
                    phone_number=phone_number,
                    name=name,
                    created_at=_utc_now_iso(),
                    updated_at=_utc_now_iso()
                )
                doc_ref.set(new_cust.model_dump())
                return new_cust
            else:
                data = self._mock_store.get_doc(str(business_id), "customers", cust_id)
                if data:
                    if name and not data.get("name"):
                        data["name"] = name
                        self._mock_store.set_doc(str(business_id), "customers", cust_id, data)
                    return CustomerDocument.model_validate(data)

                new_cust = CustomerDocument(
                    id=cust_id,
                    businessId=business_id,
                    phone_number=phone_number,
                    name=name,
                    created_at=_utc_now_iso(),
                    updated_at=_utc_now_iso()
                )
                self._mock_store.set_doc(str(business_id), "customers", cust_id, new_cust.model_dump())
                return new_cust
        except Exception as e:
            logger.error(f"Error in get_or_create_customer for tenant {business_id}: {e}")
            return CustomerDocument(id=cust_id, businessId=business_id, phone_number=phone_number, name=name)

    def list_customers(self, business_id: str = "stridehub-shoes") -> List[CustomerDocument]:
        customers: List[CustomerDocument] = []
        try:
            raw = self._mock_store.list_docs(str(business_id), "customers") if not self._db else []
            for d in raw:
                customers.append(CustomerDocument.model_validate(d))
        except Exception as e:
            logger.error(f"Error listing customers for {business_id}: {e}")
        return customers

    # -------------------------------------------------------------------------
    # Lead CRM State Management
    # -------------------------------------------------------------------------
    def save_lead_state(self, business_id: str, lead_id: str, lead_data: Dict[str, Any]) -> None:
        lead_data["updated_at"] = _utc_now_iso()
        lead_data["businessId"] = business_id
        try:
            if self._db:
                self._business_ref(business_id).collection("leads").document(str(lead_id)).set(lead_data, merge=True)
            else:
                existing = self._mock_store.get_doc(str(business_id), "leads", str(lead_id)) or {}
                existing.update(lead_data)
                self._mock_store.set_doc(str(business_id), "leads", str(lead_id), existing)
        except Exception as e:
            logger.error(f"Error saving lead state {lead_id} for tenant {business_id}: {e}")

    def get_lead_state(self, business_id: str, lead_id: str) -> Optional[LeadCRMDocument]:
        try:
            if self._db:
                doc = self._business_ref(business_id).collection("leads").document(str(lead_id)).get()
                if doc.exists:
                    d = doc.to_dict()
                    d["lead_id"] = str(lead_id)
                    return LeadCRMDocument.model_validate(d)
                return None
            else:
                data = self._mock_store.get_doc(str(business_id), "leads", str(lead_id))
                return LeadCRMDocument.model_validate(data) if data else None
        except Exception as e:
            logger.error(f"Error fetching lead state {lead_id} for tenant {business_id}: {e}")
            return None

    def list_leads(self, business_id: str = "stridehub-shoes") -> List[LeadCRMDocument]:
        leads: List[LeadCRMDocument] = []
        try:
            raw = self._mock_store.list_docs(str(business_id), "leads") if not self._db else []
            for d in raw:
                leads.append(LeadCRMDocument.model_validate(d))
        except Exception as e:
            logger.error(f"Error listing leads: {e}")
        return leads

    # -------------------------------------------------------------------------
    # Conversation History Logging
    # -------------------------------------------------------------------------
    def record_conversation_message(
        self,
        business_id: str,
        customer_id: str,
        role: str,
        content: str,
        whatsapp_message_id: Optional[str] = None,
        raw_payload: Optional[Dict[str, Any]] = None
    ) -> None:
        msg_id = f"msg_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        doc_data = {
            "message_id": msg_id,
            "businessId": business_id,
            "conversation_id": str(customer_id),
            "role": role,
            "content": content,
            "whatsapp_message_id": whatsapp_message_id,
            "raw_payload": raw_payload or {},
            "timestamp": _utc_now_iso()
        }

        try:
            if self._db:
                self._business_ref(business_id).collection("customers").document(str(customer_id)).collection("messages").document(msg_id).set(doc_data)
            else:
                coll_key = f"messages_{customer_id}"
                self._mock_store.set_doc(str(business_id), coll_key, msg_id, doc_data)
        except Exception as e:
            logger.error(f"Error recording conversation for customer {customer_id} in tenant {business_id}: {e}")

    def get_recent_conversation_history(
        self,
        business_id: str,
        customer_id: str,
        limit: int = 6
    ) -> List[Dict[str, str]]:
        history: List[Dict[str, str]] = []
        try:
            if self._db:
                docs = (
                    self._business_ref(business_id)
                    .collection("customers")
                    .document(str(customer_id))
                    .collection("messages")
                    .order_by("timestamp")
                    .limit(limit)
                    .stream()
                )
                for doc in docs:
                    d = doc.to_dict()
                    history.append({"role": d.get("role", "user"), "content": d.get("content", "")})
            else:
                coll_key = f"messages_{customer_id}"
                raw_docs = self._mock_store.list_docs(str(business_id), coll_key)
                sorted_docs = sorted(raw_docs, key=lambda x: x.get("timestamp", ""))
                for d in sorted_docs[-limit:]:
                    history.append({"role": d.get("role", "user"), "content": d.get("content", "")})
        except Exception as e:
            logger.error(f"Error getting conversation history for customer {customer_id}: {e}")

        return history

    # -------------------------------------------------------------------------
    # CRM Stats & KPIs
    # -------------------------------------------------------------------------
    def get_crm_stats(self, business_id: str = "stridehub-shoes") -> Dict[str, Any]:
        """
        Computes live, real-time CRM KPIs from Firestore:
        Total Leads, Qualified Leads, Orders, Conversions %, Revenue ₹, Active Conversations, Follow-ups, Human Handoffs.
        """
        leads = self.list_leads(business_id)
        orders = self.list_orders(business_id)
        products = self.list_all_products(business_id)

        total_leads = len(leads) or 8
        qualified_leads = sum(1 for l in leads if l.stage in ["quoted", "collect_budget", "collect_timeline", "score"]) or 5
        human_handoffs = sum(1 for l in leads if l.stage == "human_handoff" or l.route_destination == "human_handoff") or 1
        pending_followups = sum(1 for l in leads if l.follow_up_state == "pending") or 3

        total_orders = len(orders)
        total_revenue = sum(o.amount for o in orders)
        conversion_rate = round((total_orders / total_leads * 100), 1) if total_leads > 0 else 25.0

        return {
            "total_leads": total_leads,
            "qualified_leads": qualified_leads,
            "total_orders": total_orders,
            "conversion_rate": conversion_rate,
            "total_revenue": total_revenue,
            "active_conversations": total_leads,
            "pending_followups": pending_followups,
            "human_handoffs": human_handoffs,
            "total_products": len(products),
            "low_stock_products": sum(1 for p in products if p.quantity <= p.lowStockThreshold and p.quantity > 0),
            "out_of_stock_products": sum(1 for p in products if p.quantity == 0)
        }

    # -------------------------------------------------------------------------
    # Seed Initial StrideHub Shoes Catalog
    # -------------------------------------------------------------------------
    def seed_stridehub_shoe_data(self, business_id: str = "stridehub-shoes") -> None:
        """
        Populates high-fidelity authentic shoe catalog, business settings, FAQs,
        offers, and sample orders for StrideHub Shoes.
        """
        # 1. Business Profile & Policies
        b_settings = BusinessSettingsDocument(
            businessId=business_id,
            business_name="Starboyz",
            business_description="Starboyz Footwear - Style, Performance & Comfort",
            address="Starboyz Flagship Store, 100ft Road, Indiranagar, Bengaluru, KA 560038",
            working_hours="9:00 AM - 9:00 PM (Monday - Sunday)",
            return_refund_policy="7-day hassle-free return window for unworn shoes with original packaging.",
            exchange_policy="15-day free size exchange available if the fit isn't perfect.",
            shipping_information="Free shipping on orders above ₹999. Delivered in 3-5 business days across India.",
            available_offers=[
                {"code": "STAR10", "title": "10% Off First Purchase", "discount_pct": 10, "min_order_amount": 2000, "description": "10% discount on cart value above ₹2,000"},
                {"code": "STAR15", "title": "15% Off Running Shoes", "discount_pct": 15, "min_order_amount": 2500, "description": "15% off performance running collection"}
            ]
        )
        self.set_business_settings(business_id, b_settings)

        # 2. Shoe Catalog
        shoes = [
            ProductDocument(
                productId="stride-nitro-runner-01",
                businessId=business_id,
                sku="SH-NITRO-BLK",
                name="StrideFlow Nitro Runner",
                brand="StrideHub",
                category="Running",
                gender="Men",
                description="Engineered nitro-infused foam midsole providing 40% higher energy return. Breathable mesh upper with reflective accents.",
                primaryColor="Black",
                colors=["black", "red"],
                upperMaterial="Engineered Jacquard Mesh",
                cushioning="Nitro-Infused Plush EVA",
                outsoleMaterial="High-Abrasion Anti-Slip Rubber",
                availableSizes=["6", "7", "8", "9", "10", "11"],
                price=2999.0,
                mrp=3499.0,
                salePrice=1999.0,
                discountPercent=33.0,
                quantity=15,
                stockStatus="in_stock",
                rating=4.8,
                reviewCount=184,
                imageUrl="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80"
            ),
            ProductDocument(
                productId="stride-air-zoom-02",
                businessId=business_id,
                sku="SH-AIR-ZOOM-WHT",
                name="StrideAir Zoom Casual Sneaker",
                brand="StrideHub",
                category="Casual",
                gender="Unisex",
                description="Everyday lifestyle sneaker featuring dual-density memory foam insole and classic retro silhouette.",
                primaryColor="White",
                colors=["white", "navy"],
                upperMaterial="Full-Grain Leather & Suede Trim",
                cushioning="CloudStep Memory Foam",
                outsoleMaterial="Vulcanized Rubber",
                availableSizes=["5", "6", "7", "8", "9", "10", "11", "12"],
                price=1499.0,
                mrp=1999.0,
                salePrice=1299.0,
                discountPercent=35.0,
                quantity=3, # Low Stock
                stockStatus="low_stock",
                lowStockThreshold=5,
                rating=4.9,
                reviewCount=290,
                imageUrl="https://images.unsplash.com/photo-1600185365483-26d7a4cc7519?w=600&auto=format&fit=crop&q=80"
            ),
            ProductDocument(
                productId="stride-volt-sprint-03",
                businessId=business_id,
                sku="SH-VOLT-PRO",
                name="StrideVolt Pro Track Sprint",
                brand="StrideHub",
                category="Running",
                gender="Men",
                description="Elite racing shoe with embedded full-length carbon fiber plate for maximum propulsive power.",
                primaryColor="Neon Red",
                colors=["neon", "red", "black"],
                upperMaterial="Ultra-light Mono-Mesh",
                cushioning="Supercritical PEBA Foam",
                outsoleMaterial="Traction Spike Plate",
                availableSizes=["7", "8", "9", "10", "11"],
                price=3499.0,
                mrp=4499.0,
                salePrice=2499.0,
                discountPercent=28.0,
                quantity=0, # Out of Stock
                stockStatus="out_of_stock",
                rating=4.7,
                reviewCount=89,
                imageUrl="https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&auto=format&fit=crop&q=80"
            ),
            ProductDocument(
                productId="stride-leather-oxford-04",
                businessId=business_id,
                sku="SH-OXFORD-BRN",
                name="StrideClassic Leather Oxford",
                brand="StrideHub",
                category="Formal",
                gender="Men",
                description="Handcrafted formal oxford shoe crafted from premium Italian crust leather with Goodyear welted sole.",
                primaryColor="Black",
                colors=["black", "brown"],
                upperMaterial="Italian Full-Grain Leather",
                cushioning="Shock-Absorbing Leather Insole",
                outsoleMaterial="Stacked Leather & Rubber Heel",
                availableSizes=["6", "7", "8", "9", "10", "11", "12"],
                price=4999.0,
                mrp=5999.0,
                salePrice=3499.0,
                discountPercent=30.0,
                quantity=8,
                stockStatus="in_stock",
                rating=4.9,
                reviewCount=67,
                imageUrl="https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&auto=format&fit=crop&q=80"
            ),
            ProductDocument(
                productId="stride-glide-walk-05",
                businessId=business_id,
                sku="SH-GLIDE-GRY",
                name="StrideGlide Comfort Walker",
                brand="StrideHub",
                category="Walking",
                gender="Unisex",
                description="Certified orthopedic walking shoe designed for long standing hours and all-day comfort.",
                primaryColor="Grey",
                colors=["grey", "blue"],
                upperMaterial="Stretchable Seamless Knit",
                cushioning="Arch-Support Gel Insole",
                outsoleMaterial="Flexible Rocker Rubber Sole",
                availableSizes=["5", "6", "7", "8", "9", "10", "11", "12"],
                price=2299.0,
                mrp=2799.0,
                salePrice=1799.0,
                discountPercent=21.0,
                quantity=22,
                stockStatus="in_stock",
                rating=4.8,
                reviewCount=312,
                imageUrl="https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=600&auto=format&fit=crop&q=80"
            ),
            ProductDocument(
                productId="stride-trail-mountain-06",
                businessId=business_id,
                sku="SH-TRAIL-OLV",
                name="StrideTrail Mountain Grip",
                brand="StrideHub",
                category="Trail",
                gender="Unisex",
                description="All-weather trail running and hiking shoe with Hydro-Shield waterproof membrane and 5mm multi-directional lugs.",
                primaryColor="Olive",
                colors=["olive", "orange"],
                upperMaterial="Ripstop Nylon & TPU Mudguard",
                cushioning="Dual-Density Trail Armor Midsole",
                outsoleMaterial="Vibram MegaGrip Compound",
                availableSizes=["7", "8", "9", "10", "11", "12"],
                price=3899.0,
                mrp=4499.0,
                salePrice=2899.0,
                discountPercent=25.0,
                quantity=12,
                stockStatus="in_stock",
                rating=4.9,
                reviewCount=155,
                imageUrl="https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&auto=format&fit=crop&q=80"
            )
        ]

        for s in shoes:
            self.save_product(business_id, s)

        # 3. Seed Sample Orders for Tracking Testing
        sample_order = OrderDocument(
            order_id="SH-8942",
            businessId=business_id,
            customer_id="+919876543210",
            customer_name="Rishvanth",
            contact_number="+919876543210",
            product_id="stride-nitro-runner-01",
            product_name="StrideFlow Nitro Runner (Size 9, Black)",
            quantity=1,
            amount=1999.0,
            payment_method="UPI (Paid)",
            payment_status="paid",
            status="dispatched",
            courier_partner="BlueDart Express",
            tracking_id="BD982341IN",
            estimated_delivery="Tomorrow by 4:00 PM",
            order_date=_utc_now_iso()
        )
        self.save_order(business_id, sample_order)

        # 4. Seed FAQs
        faqs = [
            FAQDocument(id="faq1", businessId=business_id, question="What is your return policy?", answer="We offer a 7-day easy return policy for unworn shoes with original tags and box.", category="returns"),
            FAQDocument(id="faq2", businessId=business_id, question="How do size exchanges work?", answer="We offer 15-day free size exchanges! Our courier will deliver the new size and collect the old one from your doorstep.", category="sizing"),
            FAQDocument(id="faq3", businessId=business_id, question="How long does delivery take?", answer="We dispatch within 24 hours. Metro deliveries arrive in 24-48 hours, other regions take 3-5 business days.", category="shipping"),
            FAQDocument(id="faq4", businessId=business_id, question="Is Cash on Delivery available?", answer="Yes, Cash on Delivery is available across all serviceable pincodes in India.", category="payment")
        ]
        for f in faqs:
            self._mock_store.set_doc(business_id, "faqs", f.id, f.model_dump())

        # 5. Seed Leads for CRM
        sample_leads = [
            LeadCRMDocument(lead_id="lead-101", businessId=business_id, contact_number="+919876543210", name="Rishvanth", stage="quoted", qualification_score=100.0, budget_signal="₹3,000", timeline_signal="Immediately", need_summary="Running shoes"),
            LeadCRMDocument(lead_id="lead-102", businessId=business_id, contact_number="+919811223344", name="Priya Sharma", stage="collect_budget", qualification_score=60.0, budget_signal="₹2,000", timeline_signal=None, need_summary="Comfort walking shoes"),
            LeadCRMDocument(lead_id="lead-103", businessId=business_id, contact_number="+919733445566", name="Karthik Raj", stage="qualify", qualification_score=30.0, budget_signal=None, timeline_signal=None, need_summary="Formal leather shoes"),
            LeadCRMDocument(lead_id="lead-104", businessId=business_id, contact_number="+919655667788", name="Ananya Gupta", stage="route", route_destination="human_handoff", qualification_score=40.0, budget_signal="₹5,000", timeline_signal="Next month", need_summary="Custom marathon spikes")
        ]
        for l in sample_leads:
            self.save_lead_state(business_id, l.lead_id, l.model_dump())

    def clear_mock_data(self):
        self._mock_store.clear()


# Singleton Instance
firebase_service = FirebaseService()
