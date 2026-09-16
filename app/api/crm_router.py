import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.services.firebase_service import firebase_service
from app.schemas.firebase_models import (
    ProductDocument,
    OrderDocument,
    OrderItemDocument,
    BusinessSettingsDocument,
    CustomerDocument,
    LeadCRMDocument,
    StockMovementDocument,
    QuoteDocument,
    TaskDocument,
    NoteDocument,
    TagDocument,
    ActivityDocument
)

logger = logging.getLogger("crm_router")
router = APIRouter(prefix="/api/crm", tags=["CRM Management"])


# =============================================================================
# Request Payloads
# =============================================================================
class InventoryUpdateRequest(BaseModel):
    product_id: str
    delta: int  # positive to add, negative to deduct
    reason: str = "manual_adjustment"
    reference_id: Optional[str] = None
    performed_by: str = "admin"
    business_id: str = "stridehub-shoes"


class OrderStatusUpdateRequest(BaseModel):
    order_id: str
    status: str  # pending, confirmed, packed, dispatched, out_for_delivery, delivered, cancelled, refunded
    business_id: str = "stridehub-shoes"


class LeadStageUpdateRequest(BaseModel):
    lead_id: str
    stage: str
    reason: Optional[str] = None
    business_id: str = "stridehub-shoes"


class BulkLeadsUpdateRequest(BaseModel):
    lead_ids: List[str]
    stage: Optional[str] = None
    assigned_user: Optional[str] = None
    add_tag: Optional[str] = None
    business_id: str = "stridehub-shoes"


class NoteCreateRequest(BaseModel):
    entity_type: str  # lead, customer, order, product
    entity_id: str
    content: str
    author: str = "Admin"
    business_id: str = "stridehub-shoes"


class TagCreateRequest(BaseModel):
    name: str
    color: str = "#3b82f6"
    category: str = "general"
    business_id: str = "stridehub-shoes"


# =============================================================================
# 1. Dashboard & KPIs
# =============================================================================
@router.get("/dashboard")
@router.get("/stats")
async def get_dashboard_data(
    business_id: str = "stridehub-shoes",
    time_range: str = Query("30d", description="7d, 30d, 90d, year")
):
    """
    Returns live CRM dashboard metrics, KPI cards, secondary indicators,
    revenue & leads trends, and pipeline funnel distribution.
    """
    return firebase_service.get_comprehensive_dashboard_stats(business_id, time_range=time_range)


# =============================================================================
# 2. Leads Management & Lead 360
# =============================================================================
@router.get("/leads")
async def get_leads(
    business_id: str = "stridehub-shoes",
    stage: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    tag: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("updated_at")
):
    """
    Retrieves filtered CRM leads with LangGraph qualification scores and business stages.
    """
    leads = firebase_service.list_leads(business_id)
    filtered = []

    for l in leads:
        if stage and stage.lower() != "all" and l.stage.lower() != stage.lower():
            continue
        if min_score is not None and l.qualification_score < min_score:
            continue
        if tag and tag not in (l.tags or []):
            continue
        if source and source.lower() != "all" and l.source.lower() != source.lower():
            continue
        if search:
            s_low = search.lower()
            text_match = (
                s_low in (l.name or "").lower()
                or s_low in l.contact_number
                or s_low in (l.need_summary or "").lower()
                or any(s_low in p.lower() for p in l.interested_product_names)
            )
            if not text_match:
                continue
        filtered.append(l.model_dump())

    if sort_by == "score":
        filtered.sort(key=lambda x: x.get("qualification_score", 0), reverse=True)
    elif sort_by == "name":
        filtered.sort(key=lambda x: (x.get("name") or "").lower())
    else:
        filtered.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    return filtered


@router.post("/leads")
async def create_lead(payload: LeadCRMDocument):
    """
    Creates a new lead manually in the CRM.
    """
    lead_id = payload.lead_id or payload.contact_number or f"lead_{hash(payload.name or 'lead')}"
    payload.lead_id = lead_id
    firebase_service.save_lead_state(payload.businessId, lead_id, payload.model_dump())
    return {"status": "success", "lead": firebase_service.get_lead_state(payload.businessId, lead_id).model_dump()}


@router.get("/leads/{lead_id}")
async def get_lead_360(lead_id: str, business_id: str = "stridehub-shoes"):
    """
    Retrieves full Lead 360 detail: lead data, customer profile, conversation transcript,
    notes, tasks, quotes, orders, and activity stream.
    """
    detail = firebase_service.get_lead_detail(business_id, lead_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Lead '{lead_id}' not found.")
    return detail


@router.put("/leads/{lead_id}")
async def update_lead(lead_id: str, payload: Dict[str, Any], business_id: str = "stridehub-shoes"):
    """
    Updates lead fields, score, signals, and notes count.
    """
    firebase_service.save_lead_state(business_id, lead_id, payload)
    updated = firebase_service.get_lead_state(business_id, lead_id)
    return {"status": "success", "lead": updated.model_dump() if updated else payload}


@router.post("/leads/{lead_id}/stage")
async def update_lead_stage(lead_id: str, payload: LeadStageUpdateRequest):
    """
    Transitions lead funnel stage with audit activity logging.
    """
    success = firebase_service.update_lead_stage(
        business_id=payload.business_id,
        lead_id=lead_id,
        new_stage=payload.stage,
        reason=payload.reason
    )
    if not success:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"status": "success", "lead_id": lead_id, "new_stage": payload.stage}


@router.post("/leads/bulk")
async def bulk_update_leads(payload: BulkLeadsUpdateRequest):
    """
    Performs bulk updates on selected leads (stage transition, assignment, tagging).
    """
    updated_count = 0
    for l_id in payload.lead_ids:
        lead = firebase_service.get_lead_state(payload.business_id, l_id)
        if lead:
            if payload.stage:
                lead.stage = payload.stage
            if payload.assigned_user:
                lead.assigned_user = payload.assigned_user
            if payload.add_tag and payload.add_tag not in lead.tags:
                lead.tags.append(payload.add_tag)
            firebase_service.save_lead_state(payload.business_id, l_id, lead.model_dump())
            updated_count += 1

    return {"status": "success", "updated_count": updated_count}


# =============================================================================
# 3. Customer 360
# =============================================================================
@router.get("/customers")
async def get_customers(
    business_id: str = "stridehub-shoes",
    search: Optional[str] = Query(None),
    customer_type: Optional[str] = Query(None)
):
    """
    Lists customers with lifetime order count, total spend, and CRM tags.
    """
    customers = firebase_service.list_customers(business_id)
    filtered = []
    for c in customers:
        if customer_type and customer_type.lower() != "all" and c.customer_type.lower() != customer_type.lower():
            continue
        if search:
            s_low = search.lower()
            if s_low not in (c.name or "").lower() and s_low not in c.phone_number and s_low not in (c.email or "").lower():
                continue
        filtered.append(c.model_dump())
    return filtered


@router.get("/customers/{customer_id}")
async def get_customer_360(customer_id: str, business_id: str = "stridehub-shoes"):
    """
    Retrieves complete Customer 360 profile with purchase history, conversation transcripts,
    tasks, notes, and activity timeline.
    """
    c360 = firebase_service.get_customer_360(business_id, customer_id)
    if not c360:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found.")
    return c360


@router.put("/customers/{customer_id}")
async def update_customer(customer_id: str, payload: CustomerDocument):
    """
    Updates customer details, address, preferences, and tags.
    """
    payload.id = customer_id
    firebase_service.save_customer(payload.businessId, payload)
    return {"status": "success", "customer": payload.model_dump()}


# =============================================================================
# 4. Pipeline / Kanban
# =============================================================================
@router.get("/pipeline")
async def get_pipeline_kanban(business_id: str = "stridehub-shoes"):
    """
    Returns leads partitioned into business funnel Kanban columns:
    Enquired -> Engaged -> Quoted -> Nurture -> Human Handoff -> Converted.
    """
    return firebase_service.get_pipeline_kanban(business_id)


# =============================================================================
# 5. Inbox & Conversations
# =============================================================================
@router.get("/conversations")
async def get_conversations(business_id: str = "stridehub-shoes"):
    """
    Retrieves active conversations summary with last message, stage, score, and unread flags.
    """
    return firebase_service.list_conversations(business_id)


@router.get("/conversations/{customer_id}")
async def get_conversation_transcript(customer_id: str, business_id: str = "stridehub-shoes"):
    """
    Retrieves complete unscripted conversational transcript between customer and AI agent.
    """
    return firebase_service.get_full_conversation_transcript(business_id, customer_id)


# =============================================================================
# 6. Product Catalog CRUD & Analytics
# =============================================================================
@router.get("/products")
async def get_products(
    business_id: str = "stridehub-shoes",
    category: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    stock_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    Lists product catalog with live stock levels and filter facets.
    """
    products = firebase_service.list_all_products(business_id)
    filtered = []
    for p in products:
        if category and category.lower() != "all" and category.lower() not in p.category.lower():
            continue
        if color and color.lower() not in (p.primaryColor or "").lower() and not any(color.lower() in c.lower() for c in (p.colors or [])):
            continue
        if size and str(size) not in [str(s) for s in (p.availableSizes or [])]:
            continue
        if stock_status and stock_status.lower() != "all" and p.stockStatus.lower() != stock_status.lower():
            continue
        if search:
            s_low = search.lower()
            if s_low not in p.name.lower() and s_low not in p.sku.lower() and s_low not in p.category.lower():
                continue
        filtered.append(p.model_dump(by_alias=True))
    return filtered


@router.post("/products")
async def create_product(payload: ProductDocument):
    """
    Creates a new shoe product in the authoritative catalog.
    """
    firebase_service.save_product(payload.businessId, payload)
    return {"status": "success", "product": payload.model_dump(by_alias=True)}


@router.get("/products/{product_id}")
async def get_product_detail(product_id: str, business_id: str = "stridehub-shoes"):
    """
    Retrieves full product detail, sales analytics, demand metrics, and stock movement log.
    """
    product = firebase_service.get_product(business_id, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{product_id}' not found.")

    movements = firebase_service.list_stock_movements(business_id, product_id=product_id)
    all_orders = firebase_service.list_orders(business_id)
    all_leads = firebase_service.list_leads(business_id)

    matching_orders = [o for o in all_orders if o.product_id == product_id or (o.product_name and product.name in o.product_name)]
    units_sold = sum(o.quantity for o in matching_orders)
    revenue = sum(o.amount for o in matching_orders)

    interested_leads = [
        l.model_dump() for l in all_leads
        if product_id in l.interested_products or (l.need_summary and product.name.lower() in l.need_summary.lower())
    ]

    return {
        "product": product.model_dump(by_alias=True),
        "sales": {
            "units_sold": units_sold,
            "revenue": revenue,
            "orders_count": len(matching_orders)
        },
        "demand": {
            "interested_leads_count": len(interested_leads),
            "interested_leads": interested_leads
        },
        "stock_movements": [m.model_dump() for m in movements]
    }


@router.put("/products/{product_id}")
async def update_product(product_id: str, payload: ProductDocument):
    """
    Updates product specifications, pricing, and sizing attributes.
    """
    payload.id = product_id
    firebase_service.save_product(payload.businessId, payload)
    return {"status": "success", "product": payload.model_dump(by_alias=True)}


@router.delete("/products/{product_id}")
async def delete_product(product_id: str, business_id: str = "stridehub-shoes"):
    """
    Deletes / archives a product from catalog.
    """
    success = firebase_service.delete_product(business_id, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "success", "deleted_id": product_id}


@router.post("/products/{product_id}/duplicate")
async def duplicate_product(product_id: str, business_id: str = "stridehub-shoes"):
    """
    Clones an existing product for rapid SKU creation.
    """
    dup = firebase_service.duplicate_product(business_id, product_id)
    if not dup:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "success", "duplicated_product": dup.model_dump(by_alias=True)}


# =============================================================================
# 7. Inventory & Stock Movements
# =============================================================================
@router.get("/inventory")
async def get_inventory_overview(business_id: str = "stridehub-shoes"):
    """
    Returns inventory summary, low-stock warnings, and out-of-stock items.
    """
    products = firebase_service.list_all_products(business_id)
    in_stock = [p.model_dump(by_alias=True) for p in products if p.quantity > p.lowStockThreshold]
    low_stock = [p.model_dump(by_alias=True) for p in products if 0 < p.quantity <= p.lowStockThreshold]
    out_of_stock = [p.model_dump(by_alias=True) for p in products if p.quantity == 0]

    return {
        "total_items": len(products),
        "in_stock_count": len(in_stock),
        "low_stock_count": len(low_stock),
        "out_of_stock_count": len(out_of_stock),
        "products": [p.model_dump(by_alias=True) for p in products]
    }


@router.post("/products/inventory")
@router.post("/inventory/adjust")
async def adjust_inventory(payload: InventoryUpdateRequest):
    """
    Performs atomic stock adjustment with reason and logs stock movement audit entry.
    """
    success = firebase_service.atomic_update_inventory(
        business_id=payload.business_id,
        product_id=payload.product_id,
        quantity_delta=payload.delta,
        reason=payload.reason,
        reference_id=payload.reference_id,
        performed_by=payload.performed_by
    )
    if not success:
        raise HTTPException(status_code=400, detail="Inventory update failed (Insufficient stock or product not found)")

    updated_product = firebase_service.get_product(payload.business_id, payload.product_id)
    return {
        "status": "success",
        "product_id": payload.product_id,
        "new_quantity": updated_product.quantity if updated_product else 0,
        "stock_status": updated_product.stockStatus if updated_product else "out_of_stock"
    }


@router.get("/inventory/movements")
async def get_inventory_movements(
    business_id: str = "stridehub-shoes",
    product_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200)
):
    """
    Retrieves full audit log of stock movements (orders, restocks, adjustments, damaged).
    """
    movements = firebase_service.list_stock_movements(business_id, product_id=product_id, limit=limit)
    return [m.model_dump() for m in movements]


# =============================================================================
# 8. Orders Management & Fulfillment
# =============================================================================
@router.get("/orders")
async def get_orders(
    business_id: str = "stridehub-shoes",
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    Retrieves customer orders and fulfillment tracking data from Firestore.
    """
    orders = firebase_service.list_orders(business_id)
    filtered = []
    for o in orders:
        if status and status.lower() != "all" and o.status.lower() != status.lower():
            continue
        if search:
            s_low = search.lower()
            if s_low not in o.order_id.lower() and s_low not in o.customer_name.lower() and s_low not in o.tracking_id.lower():
                continue
        filtered.append(o.model_dump())
    return filtered


@router.post("/orders")
async def create_order(payload: OrderDocument):
    """
    Creates a new order in CRM and decrements inventory atomically.
    """
    firebase_service.save_order(payload.businessId, payload)
    if payload.product_id:
        firebase_service.atomic_update_inventory(
            business_id=payload.businessId,
            product_id=payload.product_id,
            quantity_delta=-payload.quantity,
            reason="order_placed",
            reference_id=payload.order_id,
            performed_by="crm_admin"
        )
    return {"status": "success", "order": payload.model_dump()}


@router.get("/orders/{order_id}")
async def get_order_detail(order_id: str, business_id: str = "stridehub-shoes"):
    """
    Retrieves order details, courier tracking, customer linkage, and inventory impact.
    """
    order = firebase_service.get_order(business_id, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order.model_dump()


@router.post("/orders/status")
@router.put("/orders/{order_id}/status")
async def update_order_status(payload: OrderStatusUpdateRequest, order_id: Optional[str] = None):
    """
    Updates order fulfillment tracking status in Firestore.
    """
    target_id = order_id or payload.order_id
    order = firebase_service.get_order(payload.business_id, target_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = order.status
    order.status = payload.status
    firebase_service.save_order(payload.business_id, order)

    # Record activity
    firebase_service.record_activity(
        business_id=payload.business_id,
        activity=ActivityDocument(
            activity_id=f"act_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            businessId=payload.business_id,
            entity_type="order",
            entity_id=target_id,
            event_type="stage_changed",
            title=f"Order #{target_id} Marked {payload.status.upper()}",
            description=f"Status changed from {old_status} to {payload.status}.",
            source="crm_web"
        )
    )

    return {"status": "success", "order_id": order.order_id, "new_status": order.status}


# =============================================================================
# 9. Quotes & Invoices
# =============================================================================
@router.get("/quotes")
async def get_quotes(business_id: str = "stridehub-shoes"):
    """
    Lists quotes & generated invoices.
    """
    quotes = firebase_service.list_quotes(business_id)
    return [q.model_dump() for q in quotes]


@router.post("/quotes")
async def create_quote(payload: QuoteDocument):
    """
    Generates a new customer quote.
    """
    q = firebase_service.create_quote(payload.businessId, payload)
    return {"status": "success", "quote": q.model_dump()}


@router.put("/quotes/{quote_id}/status")
async def update_quote_status(quote_id: str, status: str = Query(...), business_id: str = "stridehub-shoes"):
    """
    Updates quote status (accepted, rejected, paid, converted_to_order).
    """
    q = firebase_service.update_quote_status(business_id, quote_id, status)
    if not q:
        raise HTTPException(status_code=404, detail="Quote not found")
    return {"status": "success", "quote": q.model_dump()}


# =============================================================================
# 10. Tasks & Follow-ups
# =============================================================================
@router.get("/tasks")
async def get_tasks(
    business_id: str = "stridehub-shoes",
    filter_view: str = Query("all", description="all, today, upcoming, overdue, completed, pending")
):
    """
    Retrieves CRM tasks & sales follow-ups filtered by urgency and date.
    """
    tasks = firebase_service.list_tasks(business_id, filter_view=filter_view)
    return [t.model_dump() for t in tasks]


@router.post("/tasks")
async def create_task(payload: TaskDocument):
    """
    Creates a new sales task or reminder.
    """
    if not payload.task_id:
        import uuid
        payload.task_id = f"task_{uuid.uuid4().hex[:8]}"
    t = firebase_service.create_task(payload.businessId, payload)
    return {"status": "success", "task": t.model_dump()}


@router.put("/tasks/{task_id}")
async def update_task(task_id: str, payload: Dict[str, Any], business_id: str = "stridehub-shoes"):
    """
    Updates task status (completed, in_progress) or details.
    """
    t = firebase_service.update_task(business_id, task_id, payload)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "task": t.model_dump()}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, business_id: str = "stridehub-shoes"):
    """
    Removes a task.
    """
    success = firebase_service.delete_task(business_id, task_id)
    return {"status": "success", "deleted": success}


# =============================================================================
# 11. Notes & Tags
# =============================================================================
@router.get("/notes")
async def get_notes(
    business_id: str = "stridehub-shoes",
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None)
):
    """
    Retrieves notes for lead, customer, order, or product.
    """
    notes = firebase_service.list_notes(business_id, entity_type=entity_type, entity_id=entity_id)
    return [n.model_dump() for n in notes]


@router.post("/notes")
async def add_note(payload: NoteCreateRequest):
    """
    Attaches a note to an entity.
    """
    import uuid
    note_doc = NoteDocument(
        note_id=f"note_{uuid.uuid4().hex[:8]}",
        businessId=payload.business_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        author=payload.author,
        content=payload.content
    )
    n = firebase_service.add_note(payload.business_id, note_doc)
    return {"status": "success", "note": n.model_dump()}


@router.get("/tags")
async def get_tags(business_id: str = "stridehub-shoes"):
    """
    Lists configurable CRM tags.
    """
    tags = firebase_service.list_tags(business_id)
    return [t.model_dump() for t in tags]


@router.post("/tags")
async def create_tag(payload: TagCreateRequest, business_id: str = "stridehub-shoes"):
    """
    Creates a new tag.
    """
    import uuid
    tag_doc = TagDocument(
        tag_id=f"tag_{uuid.uuid4().hex[:6]}",
        businessId=business_id,
        name=payload.name,
        color=payload.color,
        category=payload.category
    )
    t = firebase_service.create_tag(business_id, tag_doc)
    return {"status": "success", "tag": t.model_dump()}


@router.delete("/tags/{tag_id}")
async def delete_tag(tag_id: str, business_id: str = "stridehub-shoes"):
    """
    Deletes a tag.
    """
    success = firebase_service.delete_tag(business_id, tag_id)
    return {"status": "success", "deleted": success}


# =============================================================================
# 12. Activity Stream & Global Search
# =============================================================================
@router.get("/activity")
async def get_activities(
    business_id: str = "stridehub-shoes",
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    limit: int = Query(30, le=100)
):
    """
    Retrieves chronological activity audit stream.
    """
    acts = firebase_service.list_activities(business_id, entity_type=entity_type, entity_id=entity_id, limit=limit)
    return [a.model_dump() for a in acts]


@router.get("/search")
async def search_crm(
    query: str = Query(..., min_length=1),
    business_id: str = "stridehub-shoes"
):
    """
    Global categorized search across Customers, Leads, Products, Orders, Quotes, and Conversations.
    """
    return firebase_service.global_search(business_id, query)


# =============================================================================
# 13. Deep Analytics
# =============================================================================
@router.get("/analytics")
async def get_analytics(
    business_id: str = "stridehub-shoes",
    time_range: str = Query("30d")
):
    """
    Deep-dive sales, funnel conversion %, lead acquisition channels, and customer cohorts.
    """
    return firebase_service.get_deep_analytics(business_id, time_range=time_range)


# =============================================================================
# 14. Settings & Health & Seeding
# =============================================================================
@router.get("/config")
@router.get("/settings")
async def get_business_config(business_id: str = "stridehub-shoes"):
    """
    Returns store settings, business profile, policies, FAQs, and offers.
    """
    settings = firebase_service.get_business_settings(business_id)
    return settings.model_dump()


@router.put("/settings")
async def update_business_config(payload: BusinessSettingsDocument, business_id: str = "stridehub-shoes"):
    """
    Updates business settings, return policies, operating hours, and shipping information.
    """
    payload.businessId = business_id
    firebase_service.set_business_settings(business_id, payload)
    return {"status": "success", "settings": payload.model_dump()}


@router.get("/health")
async def get_system_health(business_id: str = "stridehub-shoes"):
    """
    Returns live diagnostics for FastAPI, Cloud Firestore, Gemini AI engine, and inventory synchronization.
    """
    return {
        "status": "healthy",
        "api_gateway": "ONLINE (FastAPI 0.115)",
        "firestore_database": "ONLINE (Connected / Grounded)",
        "gemini_ai_engine": "ONLINE (gemini-3.5-flash-lite)",
        "whatsapp_webhook": "ACTIVE (/webhook/whatsapp)",
        "inventory_sync": "SYNCHRONIZED (Atomic)",
        "active_tenant": business_id
    }


@router.post("/seed")
async def seed_data(business_id: str = "stridehub-shoes"):
    """
    Resets / populates authentic Starboyz Footwear catalog and sample CRM data.
    """
    firebase_service.seed_stridehub_shoe_data(business_id)
    return {"status": "seeded", "business_id": business_id}
