import uuid
import pytest
from app.services.firebase_service import firebase_service
from app.schemas.firebase_models import ProductDocument, CustomerDocument, BusinessSettingsDocument


def test_01_business_a_cannot_access_business_b_products():
    """
    Test: Business A product catalog is completely isolated from Business B in Firebase.
    """
    biz_a = "business-tenant-alpha"
    biz_b = "business-tenant-beta"

    # Business A has Solar Inverter
    prod_a = ProductDocument(
        id="solar-inv-5kw",
        name="5kW Hybrid Solar Inverter",
        price=75000.0,
        available_quantity=10,
        category="Solar"
    )
    firebase_service.save_product(biz_a, prod_a)

    # Business B has Luxury Watch
    prod_b = ProductDocument(
        id="watch-chronograph",
        name="Automatic Chronograph Watch",
        price=25000.0,
        available_quantity=5,
        category="Watches"
    )
    firebase_service.save_product(biz_b, prod_b)

    # Querying under Business A should NEVER return Business B's watch
    results_a = firebase_service.search_products(biz_a, query="watch")
    assert len(results_a) == 0

    # Querying under Business B should NEVER return Business A's solar inverter
    results_b = firebase_service.search_products(biz_b, query="solar")
    assert len(results_b) == 0

    # Direct document lookup isolation
    assert firebase_service.get_product(biz_a, "watch-chronograph") is None
    assert firebase_service.get_product(biz_b, "solar-inv-5kw") is None


def test_02_customer_a_cannot_access_customer_b_conversations():
    """
    Test: Conversation history of Customer A cannot leak into Customer B's context.
    """
    biz_id = f"business-tenant-gamma-{uuid.uuid4().hex[:6]}"
    cust_a_id = f"customer-1001-{uuid.uuid4().hex[:6]}"
    cust_b_id = f"customer-1002-{uuid.uuid4().hex[:6]}"

    # Customer A talks about personal medical equipment
    firebase_service.record_conversation_message(
        business_id=biz_id,
        customer_id=cust_a_id,
        role="user",
        content="Inquiring about CPAP medical device prescription"
    )

    # Customer B talks about office furniture
    firebase_service.record_conversation_message(
        business_id=biz_id,
        customer_id=cust_b_id,
        role="user",
        content="Need 20 ergonomic office chairs"
    )

    history_a = firebase_service.get_recent_conversation_history(biz_id, cust_a_id)
    history_b = firebase_service.get_recent_conversation_history(biz_id, cust_b_id)

    assert len(history_a) == 1
    assert "CPAP" in history_a[0]["content"]
    assert "chairs" not in history_a[0]["content"]

    assert len(history_b) == 1
    assert "chairs" in history_b[0]["content"]
    assert "CPAP" not in history_b[0]["content"]


def test_03_business_settings_isolation():
    """
    Test: Business A's custom policies and offers are isolated from Business B.
    """
    biz_x = "tenant-retail-x"
    biz_y = "tenant-retail-y"

    settings_x = BusinessSettingsDocument(
        business_name="Store X",
        return_refund_policy="15-day refund policy",
        available_offers=[{"code": "X15", "discount_pct": 15}]
    )
    firebase_service.set_business_settings(biz_x, settings_x)

    settings_y = BusinessSettingsDocument(
        business_name="Store Y",
        return_refund_policy="No returns or exchanges",
        available_offers=[]
    )
    firebase_service.set_business_settings(biz_y, settings_y)

    retrieved_x = firebase_service.get_business_settings(biz_x)
    retrieved_y = firebase_service.get_business_settings(biz_y)

    assert retrieved_x.business_name == "Store X"
    assert "15-day" in retrieved_x.return_refund_policy
    assert len(retrieved_x.available_offers) == 1

    assert retrieved_y.business_name == "Store Y"
    assert "No returns" in retrieved_y.return_refund_policy
    assert len(retrieved_y.available_offers) == 0
