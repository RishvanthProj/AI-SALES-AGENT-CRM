import pytest
from datetime import datetime, timezone
from app.services.firebase_service import firebase_service
from app.schemas.firebase_models import (
    ProductDocument,
    CustomerDocument,
    LeadCRMDocument,
    OrderDocument,
    QuoteDocument,
    TaskDocument,
    StockMovementDocument
)


@pytest.fixture(autouse=True)
def setup_crm_environment():
    """Initializes a fresh isolated CRM database environment before each test."""
    firebase_service.clear_mock_data()
    firebase_service.seed_stridehub_shoe_data("stridehub-shoes")
    yield


def test_authoritative_product_and_inventory_source():
    """Verify that products and stock levels are grounded and authoritative."""
    products = firebase_service.list_all_products("stridehub-shoes")
    assert len(products) >= 6

    # Test Nitro Runner
    nitro = firebase_service.get_product("stridehub-shoes", "stride-nitro-runner-01")
    assert nitro is not None
    assert nitro.price == 2999.0
    assert nitro.salePrice == 1999.0
    assert nitro.effective_price == 1999.0
    assert nitro.quantity == 15


def test_atomic_inventory_update_and_audit_logging():
    """Verify that inventory adjustments update stock atomically and record an audit movement."""
    initial_product = firebase_service.get_product("stridehub-shoes", "stride-nitro-runner-01")
    initial_stock = initial_product.quantity

    # 1. Deduct 2 units (simulate order)
    success = firebase_service.atomic_update_inventory(
        business_id="stridehub-shoes",
        product_id="stride-nitro-runner-01",
        quantity_delta=-2,
        reason="order_placed",
        reference_id="TEST-ORD-01",
        performed_by="terminal_chat"
    )
    assert success is True

    updated_product = firebase_service.get_product("stridehub-shoes", "stride-nitro-runner-01")
    assert updated_product.quantity == initial_stock - 2

    # 2. Check stock movements audit log
    movements = firebase_service.list_stock_movements("stridehub-shoes", product_id="stride-nitro-runner-01")
    assert len(movements) >= 1
    recent = movements[0]
    assert recent.quantity_change == -2
    assert recent.previous_quantity == initial_stock
    assert recent.new_quantity == initial_stock - 2
    assert recent.reason == "order_placed"
    assert recent.reference_id == "TEST-ORD-01"

    # 3. Negative inventory prevention: Try deducting 100 units
    impossible = firebase_service.atomic_update_inventory(
        business_id="stridehub-shoes",
        product_id="stride-nitro-runner-01",
        quantity_delta=-100
    )
    assert impossible is False
    unchanged_product = firebase_service.get_product("stridehub-shoes", "stride-nitro-runner-01")
    assert unchanged_product.quantity == initial_stock - 2


def test_customer_360_lifetime_spend_and_order_aggregation():
    """Verify that Customer 360 accurately aggregates lifetime purchases, total spend, and AOV."""
    cust_id = "+919876543210"

    # Save a second order for this customer
    order2 = OrderDocument(
        order_id="TEST-ORD-02",
        businessId="stridehub-shoes",
        customer_id=cust_id,
        customer_name="Rishvanth",
        contact_number=cust_id,
        product_id="stride-glide-walk-05",
        product_name="StrideGlide Comfort Walker",
        quantity=1,
        amount=1799.0,
        payment_method="UPI",
        payment_status="paid",
        status="confirmed",
        order_date=datetime.now(timezone.utc).isoformat()
    )
    firebase_service.save_order("stridehub-shoes", order2)

    # Fetch Customer 360 profile
    c360 = firebase_service.get_customer_360("stridehub-shoes", cust_id)
    assert c360 is not None
    assert c360["customer"]["total_orders"] >= 2
    assert c360["customer"]["total_spent"] >= (1999.0 + 1799.0)
    assert c360["customer"]["customer_type"] == "high_value"
    assert len(c360["orders"]) >= 2


def test_lead_pipeline_kanban_stage_mapping():
    """Verify that leads are correctly partitioned into CRM business pipeline columns."""
    kanban = firebase_service.get_pipeline_kanban("stridehub-shoes")
    assert "enquired" in kanban
    assert "engaged" in kanban
    assert "quoted" in kanban
    assert "nurture" in kanban
    assert "human_handoff" in kanban
    assert "converted" in kanban

    # Check converted lead
    assert any(l["contact_number"] == "+919876543210" for l in kanban["converted"])
    # Check human handoff lead
    assert any(l["contact_number"] == "+919655667788" for l in kanban["human_handoff"])


def test_quotes_and_invoices_lifecycle():
    """Verify quote generation, acceptance, and invoice creation."""
    quote = QuoteDocument(
        quote_id="QU-8812",
        businessId="stridehub-shoes",
        customer_id="+919811223344",
        customer_name="Priya Sharma",
        contact_number="+919811223344",
        subtotal=1999.0,
        discount=200.0,
        total_amount=1799.0,
        status="draft"
    )
    created = firebase_service.create_quote("stridehub-shoes", quote)
    assert created.quote_id == "QU-8812"

    # Accept quote
    accepted = firebase_service.update_quote_status("stridehub-shoes", "QU-8812", "accepted")
    assert accepted is not None
    assert accepted.status == "accepted"
    assert accepted.invoice_id is not None
    assert accepted.invoice_id.startswith("INV-")


def test_global_categorized_search():
    """Verify that search returns matches categorized across leads, products, orders, and conversations."""
    results = firebase_service.global_search("stridehub-shoes", "Runner")
    assert len(results["products"]) >= 1
    assert any("Runner" in p["title"] for p in results["products"])

    results_cust = firebase_service.global_search("stridehub-shoes", "Rishvanth")
    assert len(results_cust["customers"]) >= 1 or len(results_cust["leads"]) >= 1


def test_dashboard_and_analytics_kpi_computation():
    """Verify live CRM KPIs and metrics are computed from real Firestore data."""
    stats = firebase_service.get_comprehensive_dashboard_stats("stridehub-shoes")
    kpis = stats["kpis"]
    assert kpis["total_leads"] >= 4
    assert kpis["total_orders"] >= 1
    assert kpis["total_revenue"] >= 1999.0
    assert len(stats["charts"]["revenue_trend"]) > 0
    assert len(stats["charts"]["leads_trend"]) > 0
