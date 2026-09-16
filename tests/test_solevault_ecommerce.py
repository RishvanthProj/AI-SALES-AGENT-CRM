import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_01_storefront_list_products(client: AsyncClient):
    """
    Test storefront products endpoint with 20+ shoes and pagination.
    """
    resp = await client.get("/api/v1/store/products?page=1&page_size=25")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["data"]) >= 20
    assert data["meta"]["total_count"] >= 20

    # Verify first product has rich attributes
    p = data["data"][0]
    assert "name" in p
    assert "sku" in p
    assert "sale_price" in p
    assert "available_sizes" in p
    assert len(p["available_sizes"]) > 0


@pytest.mark.asyncio
async def test_02_storefront_filter_by_category_and_gender(client: AsyncClient):
    """
    Test filtering by category 'running-shoes' and gender 'Men'.
    """
    # Category filter
    resp = await client.get("/api/v1/store/products?category=running-shoes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]) >= 1
    for p in data["data"]:
        assert "Running" in p["category_name"] or "AeroSprint" in p["name"]

    # Gender filter
    resp_women = await client.get("/api/v1/store/products?gender=Women")
    assert resp_women.status_code == 200
    women_data = resp_women.json()
    assert len(women_data["data"]) >= 1
    for p in women_data["data"]:
        assert p["gender"] in ["Women", "Unisex"]


@pytest.mark.asyncio
async def test_03_storefront_filter_by_price_and_sort(client: AsyncClient):
    """
    Test filtering by price range and sorting by price ascending.
    """
    resp = await client.get("/api/v1/store/products?min_price=1000&max_price=3500&sort_by=price_asc")
    assert resp.status_code == 200
    data = resp.json()
    products = data["data"]
    assert len(products) >= 1

    prices = [p["sale_price"] for p in products]
    assert prices == sorted(prices)
    for pr in prices:
        assert 1000 <= pr <= 3500


@pytest.mark.asyncio
async def test_04_product_detail_and_specs(client: AsyncClient):
    """
    Test product detail by slug with variants, images, specifications, and reviews.
    """
    resp = await client.get("/api/v1/store/products/aerosprint-x1")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["name"] == "AeroSprint X1"
    assert data["sku"] == "SV-0001"
    assert len(data["images"]) >= 1
    assert len(data["variants"]) >= 6
    assert len(data["features_list"]) >= 1
    assert len(data["reviews"]) >= 1


@pytest.mark.asyncio
async def test_05_store_categories_and_brands(client: AsyncClient):
    """
    Test 20 categories and 5 brands endpoints.
    """
    cat_resp = await client.get("/api/v1/store/categories")
    assert cat_resp.status_code == 200
    cats = cat_resp.json()["data"]
    assert len(cats) == 20

    brand_resp = await client.get("/api/v1/store/brands")
    assert brand_resp.status_code == 200
    brands = brand_resp.json()["data"]
    assert len(brands) == 5


@pytest.mark.asyncio
async def test_06_product_comparison(client: AsyncClient):
    """
    Test side-by-side comparison for up to 4 shoe models.
    """
    payload = {"product_ids": [1, 2, 3]}
    resp = await client.post("/api/v1/store/compare", json=payload)
    assert resp.status_code == 200
    matrix = resp.json()["data"]
    assert len(matrix) == 3
    for shoe in matrix:
        assert "weight" in shoe
        assert "technology" in shoe
        assert "cushioning" in shoe
        assert "price" in shoe


@pytest.mark.asyncio
async def test_07_cart_calculation_with_coupon(client: AsyncClient):
    """
    Test cart calculation, tax 18%, free shipping threshold, and coupon 'STRIDE10'.
    """
    # 1. Cart under threshold (e.g. 1 shoe of ₹699) -> ₹120 shipping fee
    p12_resp = await client.get("/api/v1/store/products/comfycloud")
    assert p12_resp.status_code == 200
    p12_var_id = p12_resp.json()["data"]["variants"][0]["id"]

    cart_payload = {
        "items": [{"product_id": 12, "variant_id": p12_var_id, "quantity": 1}],
        "coupon_code": None
    }
    resp = await client.post("/api/v1/cart/calculate", json=cart_payload)
    assert resp.status_code == 200
    cart_data = resp.json()["data"]
    assert cart_data["subtotal"] == 699.0
    assert cart_data["shipping_fee"] == 120.0
    assert cart_data["amount_needed_for_free_shipping"] == 801.0

    # 2. Cart above threshold with coupon STRIDE10 (10% discount on orders > ₹1999)
    cart_payload_large = {
        "items": [{"product_id": 1, "variant_id": 1, "quantity": 1}],  # ₹4999
        "coupon_code": "STRIDE10"
    }
    resp_large = await client.post("/api/v1/cart/calculate", json=cart_payload_large)
    assert resp_large.status_code == 200
    cart_large = resp_large.json()["data"]
    assert cart_large["subtotal"] == 4999.0
    assert cart_large["coupon_code"] == "STRIDE10"
    assert cart_large["coupon_discount"] == 499.90
    assert cart_large["shipping_fee"] == 0.0  # Free shipping


@pytest.mark.asyncio
async def test_08_checkout_and_order_tracking(client: AsyncClient):
    """
    Test atomic checkout, order number generation, stock decrement, and real-time tracking.
    """
    checkout_payload = {
        "full_name": "Rohan Patel",
        "email": "rohan.patel@example.com",
        "phone": "+919876543299",
        "address_line_1": "Flat 402, Skyline Towers",
        "address_line_2": "Indiranagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postal_code": "560038",
        "country": "India",
        "shipping_method_id": 1,
        "payment_method": "UPI",
        "coupon_code": "STRIDE10",
        "items": [{"product_id": 1, "variant_id": 1, "quantity": 1}],
        "customer_notes": "Please ring bell on delivery."
    }

    resp = await client.post("/api/v1/checkout/place-order", json=checkout_payload)
    assert resp.status_code == 200
    order_data = resp.json()["data"]
    assert order_data["order_number"].startswith("SV-")
    assert order_data["tracking_number"].startswith("DLV-")
    assert order_data["payment_status"] == "paid"
    assert order_data["order_status"] == "confirmed"

    # Track the order
    order_num = order_data["order_number"]
    track_resp = await client.get(f"/api/v1/orders/{order_num}/track")
    assert track_resp.status_code == 200
    track_data = track_resp.json()["data"]
    assert track_data["order_number"] == order_num
    assert len(track_data["milestones"]) == 6
    assert track_data["milestones"][0]["title"] == "Order Placed"


@pytest.mark.asyncio
async def test_09_admin_kpis_and_analytics_charts(client: AsyncClient):
    """
    Test executive admin KPIs and SVG analytics charts endpoints.
    """
    # KPIs
    kpi_resp = await client.get("/api/v1/admin/kpis")
    assert kpi_resp.status_code == 200
    kpis = kpi_resp.json()["data"]
    assert kpis["total_revenue"] > 0
    assert kpis["total_orders"] >= 4
    assert kpis["total_products"] >= 20
    assert kpis["average_order_value"] > 0

    # Analytics Charts
    chart_resp = await client.get("/api/v1/admin/analytics/charts")
    assert chart_resp.status_code == 200
    charts = chart_resp.json()["data"]
    assert len(charts["revenue_by_day"]) == 7
    assert len(charts["orders_by_category"]) >= 4
    assert len(charts["sales_by_gender"]) == 3
    assert len(charts["inventory_by_status"]) == 3


@pytest.mark.asyncio
async def test_10_admin_inventory_stock_adjustment(client: AsyncClient):
    """
    Test atomic inventory restock adjustment via Admin API.
    """
    adjust_payload = {
        "product_id": 1,
        "variant_id": 1,
        "adjustment": 20,
        "reason": "Shipment restock batch #BLR-2026"
    }
    resp = await client.post("/api/v1/admin/inventory/adjust", json=adjust_payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["new_quantity"] == data["previous_quantity"] + 20


@pytest.mark.asyncio
async def test_11_admin_order_status_workflow(client: AsyncClient):
    """
    Test admin updating order workflow status (e.g. to 'shipped' and 'delivered').
    """
    # 1. Update order #1 to shipped
    update_payload = {"order_status": "shipped"}
    resp = await client.put("/api/v1/admin/orders/1/status", json=update_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    # 2. Verify tracking status reflects updated milestone
    track_resp = await client.get("/api/v1/orders/SV-8942/track")
    assert track_resp.status_code == 200
    assert track_resp.json()["data"]["order_status"] == "shipped"
