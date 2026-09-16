from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, desc
from sqlalchemy.orm import selectinload


def _now() -> datetime:
    return datetime.now(timezone.utc)

from app.db.session import get_db
from app.db.solevault_models import (
    Product,
    ProductVariant,
    ProductImage,
    Category,
    Brand,
    Order,
    OrderItem,
    User,
    Coupon,
    Review,
    ReviewHelpfulness,
    Return,
    Banner
)
from app.schemas.solevault_schemas import (
    ProductListItemDTO,
    ProductDetailDTO,
    CategoryDTO,
    BrandDTO,
    CartDTO,
    CheckoutRequest,
    OrderResponseDTO,
    ReviewCreateDTO,
    ReviewVoteDTO,
    CompareRequestDTO,
    AdminKpisDTO,
    AnalyticsChartDTO
)
from app.services.solevault_service import solevault_service
from app.db.seed_solevault import seed_solevault_database

router = APIRouter(prefix="/api/v1", tags=["SOLEVAULT E-Commerce"])


# =============================================================================
# 1. STOREFRONT CATALOG & PRODUCTS
# =============================================================================
@router.get("/store/products")
async def list_products(
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    sport: Optional[str] = Query(None),
    occasion: Optional[str] = Query(None),
    size: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    brand: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_rating: Optional[float] = Query(None),
    water_resistant: Optional[bool] = Query(None),
    waterproof: Optional[bool] = Query(None),
    breathable: Optional[bool] = Query(None),
    featured: Optional[bool] = Query(None),
    best_seller: Optional[bool] = Query(None),
    new_arrival: Optional[bool] = Query(None),
    limited_edition: Optional[bool] = Query(None),
    in_stock_only: Optional[bool] = Query(False),
    query: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("recommended"),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves filtered footwear products with pagination and 15+ filter facets.
    """
    products, total_count = await solevault_service.get_products(
        session=db,
        category=category,
        subcategory=subcategory,
        gender=gender,
        sport=sport,
        occasion=occasion,
        size=size,
        color=color,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        water_resistant=water_resistant,
        waterproof=waterproof,
        breathable=breathable,
        featured=featured,
        best_seller=best_seller,
        new_arrival=new_arrival,
        limited_edition=limited_edition,
        in_stock_only=in_stock_only,
        query=query,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )

    return {
        "status": "success",
        "data": products,
        "meta": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": (total_count + page_size - 1) // page_size if page_size > 0 else 1
        }
    }


@router.get("/store/products/{identifier}")
async def get_product_detail(identifier: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieves complete product specification, sizing variants, high-res images, and verified reviews.
    """
    product = await solevault_service.get_product_by_id_or_slug(db, identifier)
    if not product:
        raise HTTPException(status_code=404, detail="Shoe product not found")

    return {"status": "success", "data": product}


@router.get("/store/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    """
    Retrieves all 20 shoe categories.
    """
    categories = await solevault_service.get_categories(db)
    return {"status": "success", "data": categories}


@router.get("/store/brands")
async def get_brands(db: AsyncSession = Depends(get_db)):
    """
    Retrieves footwear brand profiles.
    """
    brands = await solevault_service.get_brands(db)
    return {"status": "success", "data": brands}


@router.get("/store/search")
async def search_autocomplete(q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)):
    """
    Instant search suggestions and popular keywords.
    """
    products, _ = await solevault_service.get_products(db, query=q, page=1, page_size=6)
    return {
        "status": "success",
        "query": q,
        "suggestions": [p.name for p in products],
        "results": products
    }


@router.post("/store/compare")
async def compare_shoes(req: CompareRequestDTO, db: AsyncSession = Depends(get_db)):
    """
    Side-by-side comparison matrix for up to 4 shoe models.
    """
    matrix = await solevault_service.compare_products(db, req.product_ids)
    return {"status": "success", "data": matrix}


@router.get("/store/offers")
async def get_offers(db: AsyncSession = Depends(get_db)):
    """
    Active store coupons and promotional banners.
    """
    stmt = select(Coupon).where(Coupon.status == "active")
    res = await db.execute(stmt)
    coupons = res.scalars().all()

    b_stmt = select(Banner).where(Banner.status == "active").order_by(Banner.display_order)
    b_res = await db.execute(b_stmt)
    banners = b_res.scalars().all()

    return {
        "status": "success",
        "coupons": [
            {
                "code": c.code,
                "description": c.description,
                "discount_type": c.discount_type,
                "discount_value": c.discount_value,
                "minimum_order_amount": float(c.minimum_order_amount),
            }
            for c in coupons
        ],
        "banners": [
            {
                "title": b.title,
                "subtitle": b.subtitle,
                "image_url": b.image_url,
                "button_text": b.button_text,
                "button_url": b.button_url
            }
            for b in banners
        ]
    }


# =============================================================================
# 2. CART & CHECKOUT
# =============================================================================
@router.post("/cart/calculate")
async def calculate_cart_totals(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Calculates subtotal, discounts, coupon savings, 18% tax, and free shipping progress.
    """
    items = payload.get("items", [])
    coupon_code = payload.get("coupon_code")
    cart = await solevault_service.calculate_cart(db, items, coupon_code)
    return {"status": "success", "data": cart}


@router.post("/checkout/place-order")
async def place_order(req: CheckoutRequest, db: AsyncSession = Depends(get_db)):
    """
    Processes customer checkout, decrements inventory atomically, and generates live tracking ID.
    """
    try:
        order_resp = await solevault_service.place_order(db, req)
        return {"status": "success", "data": order_resp}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail="Error processing checkout order")


@router.get("/orders/{order_number}/track")
async def track_order(order_number: str, db: AsyncSession = Depends(get_db)):
    """
    Live delivery tracking milestones for any SOLEVAULT order.
    """
    tracking = await solevault_service.track_order(db, order_number)
    if not tracking:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"status": "success", "data": tracking}


# =============================================================================
# 3. REVIEWS & RATINGS
# =============================================================================
@router.post("/store/products/{product_id}/reviews")
async def add_review(product_id: int, req: ReviewCreateDTO, db: AsyncSession = Depends(get_db)):
    """
    Submits a verified product review.
    """
    review = Review(
        product_id=product_id,
        rating=req.rating,
        title=req.title,
        review_text=req.review_text,
        verified_purchase=True,
        helpful_count=0,
        status="approved"
    )
    db.add(review)
    await db.commit()
    return {"status": "success", "message": "Review submitted successfully!"}


# =============================================================================
# 4. ADMIN & ANALYTICS SUITE
# =============================================================================
@router.get("/admin/kpis")
async def get_admin_kpis(db: AsyncSession = Depends(get_db)):
    """
    Real-time revenue, orders, inventory alerts, and AOV metrics.
    """
    kpis = await solevault_service.get_admin_kpis(db)
    return {"status": "success", "data": kpis}


@router.get("/admin/analytics/charts")
async def get_analytics_charts(db: AsyncSession = Depends(get_db)):
    """
    Interactive chart time-series data for dashboard visualization.
    """
    charts = await solevault_service.get_analytics_charts(db)
    return {"status": "success", "data": charts}


@router.get("/admin/products")
async def admin_list_products(db: AsyncSession = Depends(get_db)):
    """
    Admin catalog table with stock status and variant counts.
    """
    stmt = (
        select(Product)
        .where(Product.deleted_at.is_(None))
        .options(
            selectinload(Product.brand),
            selectinload(Product.category),
            selectinload(Product.variants)
        )
        .order_by(Product.id)
    )
    res = await db.execute(stmt)
    products = res.scalars().all()

    return {
        "status": "success",
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "category": p.category.name if p.category else "Unassigned",
                "brand": p.brand.name if p.brand else "SOLEVAULT",
                "sale_price": float(p.sale_price),
                "mrp": float(p.mrp),
                "stock": p.available_quantity,
                "variants_count": len(p.variants),
                "featured": p.featured,
                "best_seller": p.best_seller,
                "new_arrival": p.new_arrival,
                "rating": float(p.rating_average),
                "status": p.status
            }
            for p in products
        ]
    }


@router.post("/admin/inventory/adjust")
async def adjust_stock(payload: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """
    Atomically updates shoe variant inventory and logs audit transaction.
    """
    p_id = int(payload.get("product_id", 0))
    v_id = int(payload.get("variant_id", 0))
    adjustment = int(payload.get("adjustment", 0))
    reason = str(payload.get("reason", "Admin manual restock"))

    try:
        res = await solevault_service.adjust_inventory(db, p_id, v_id, adjustment, reason)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/orders")
async def admin_list_orders(
    status_filter: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Admin order queue with customer and shipping summary.
    """
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.user),
            selectinload(Order.shipping_address)
        )
        .order_by(desc(Order.id))
    )
    if status_filter and status_filter != "all":
        stmt = stmt.where(Order.order_status == status_filter)

    res = await db.execute(stmt)
    orders = res.scalars().all()

    return {
        "status": "success",
        "data": [
            {
                "id": o.id,
                "order_number": o.order_number,
                "customer_name": o.user.full_name if o.user else (o.shipping_address.recipient_name if o.shipping_address else "Customer"),
                "email": o.user.email if o.user else "guest@solevault.com",
                "total": float(o.total),
                "payment_status": o.payment_status,
                "order_status": o.order_status,
                "shipping_status": o.shipping_status,
                "tracking_number": o.tracking_number,
                "items_count": len(o.items),
                "placed_at": o.placed_at.strftime("%b %d, %Y %I:%M %p")
            }
            for o in orders
        ]
    }


@router.put("/admin/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    payload: Dict[str, str],
    db: AsyncSession = Depends(get_db)
):
    """
    Updates workflow state (confirmed, processing, packed, shipped, delivered, cancelled).
    """
    new_status = payload.get("order_status")
    if not new_status:
        raise HTTPException(status_code=400, detail="New order_status is required")

    await db.execute(
        update(Order)
        .where(Order.id == order_id)
        .values(
            order_status=new_status,
            updated_at=_now(),
            shipped_at=_now() if new_status == "shipped" else None,
            delivered_at=_now() if new_status == "delivered" else None
        )
    )
    await db.commit()
    return {"status": "success", "message": f"Order #{order_id} updated to '{new_status}'"}


@router.post("/admin/seed")
async def trigger_seed(db: AsyncSession = Depends(get_db)):
    """
    Seeds/resets the SOLEVAULT database with authentic demo data.
    """
    result = await seed_solevault_database(db)
    return {"status": "success", "data": result}
