import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.firebase_service import firebase_service
from app.schemas.firebase_models import ProductDocument, OrderDocument, BusinessSettingsDocument

logger = logging.getLogger("crm_router")
router = APIRouter(prefix="/api/crm", tags=["CRM Management"])


class InventoryUpdateRequest(BaseModel):
    product_id: str
    delta: int # positive to add, negative to deduct
    business_id: str = "stridehub-shoes"


class OrderStatusUpdateRequest(BaseModel):
    order_id: str
    status: str # pending, confirmed, dispatched, out_for_delivery, delivered, cancelled
    business_id: str = "stridehub-shoes"


@router.get("/stats")
async def get_crm_stats(business_id: str = "stridehub-shoes"):
    """
    Returns real-time CRM KPIs computed directly from Firestore.
    """
    return firebase_service.get_crm_stats(business_id)


@router.get("/products")
async def get_products(
    business_id: str = "stridehub-shoes",
    category: Optional[str] = None,
    color: Optional[str] = None,
    size: Optional[str] = None
):
    """
    Lists StrideHub shoe catalog with real-time stock levels.
    """
    products = firebase_service.list_all_products(business_id)
    filtered = []
    for p in products:
        if category and category.lower() != "all" and category.lower() not in p.category.lower():
            continue
        if color and color.lower() not in (p.primaryColor or "").lower() and not any(color.lower() in c.lower() for c in (p.colors or [])):
            continue
        if size and size not in (p.availableSizes or []):
            continue
        filtered.append(p.model_dump(by_alias=True))
    return filtered


@router.post("/products/inventory")
async def update_inventory(payload: InventoryUpdateRequest):
    """
    Performs atomic stock increment/decrement in Firestore.
    """
    success = firebase_service.atomic_update_inventory(
        business_id=payload.business_id,
        product_id=payload.product_id,
        quantity_delta=payload.delta
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


@router.get("/leads")
async def get_leads(business_id: str = "stridehub-shoes"):
    """
    Retrieves all CRM leads with their current LangGraph qualification stage and score.
    """
    leads = firebase_service.list_leads(business_id)
    return [l.model_dump() for l in leads]


@router.get("/orders")
async def get_orders(business_id: str = "stridehub-shoes"):
    """
    Retrieves all customer orders and fulfillment tracking data from Firestore.
    """
    orders = firebase_service.list_orders(business_id)
    return [o.model_dump() for o in orders]


@router.post("/orders/status")
async def update_order_status(payload: OrderStatusUpdateRequest):
    """
    Updates order fulfillment tracking status in Firestore.
    """
    order = firebase_service.get_order(payload.business_id, payload.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    firebase_service.save_order(payload.business_id, order)
    return {"status": "success", "order_id": order.order_id, "new_status": order.status}


@router.get("/config")
async def get_business_config(business_id: str = "stridehub-shoes"):
    """
    Returns StrideHub store settings, business profile, policies, FAQs, and offers.
    """
    settings = firebase_service.get_business_settings(business_id)
    return settings.model_dump()


@router.post("/seed")
async def seed_data(business_id: str = "stridehub-shoes"):
    """
    Initializes/resets StrideHub Shoes data in Firestore.
    """
    firebase_service.seed_stridehub_shoe_data(business_id)
    return {"status": "seeded", "business_id": business_id}
