import pytest
from app.services.firebase_service import firebase_service
from app.services.validation_service import validation_service
from app.services.whatsapp_service import WhatsAppService
from app.schemas.firebase_models import ProductDocument, ProductVariant, BusinessSettingsDocument


@pytest.fixture(autouse=True)
def setup_mock_firebase_data():
    """
    Populate isolated mock Firebase test data for tenant-test-biz.
    """
    firebase_service.clear_mock_data()

    # Create Formal Shirt in Firebase
    shirt = ProductDocument(
        id="prod-shirt-001",
        name="Formal Cotton Shirt",
        description="Premium slim fit cotton shirt",
        sku="SHIRT-COT-BLK",
        category="Apparel",
        price=1499.0,
        sale_price=1299.0,
        available_quantity=27,
        stock_status="in_stock",
        sizes=["S", "M", "L", "XL"],
        colors=["black", "blue", "white"],
        variants=[
            ProductVariant(variant_id="v1", size="S", color="black", stock=5),
            ProductVariant(variant_id="v2", size="M", color="black", stock=10),
            ProductVariant(variant_id="v3", size="L", color="black", stock=8),
            ProductVariant(variant_id="v4", size="XL", color="black", stock=4),
        ]
    )
    firebase_service.save_product("tenant-test-biz", shirt)

    # Create Out of Stock Blazer in Firebase
    blazer = ProductDocument(
        id="prod-blazer-002",
        name="Navy Blue Blazer",
        description="Double breasted wool blazer",
        sku="BLAZER-NVY",
        category="Apparel",
        price=4999.0,
        sale_price=3999.0,
        available_quantity=0,
        stock_status="out_of_stock",
        sizes=["38", "40", "42"],
        colors=["navy"]
    )
    firebase_service.save_product("tenant-test-biz", blazer)

    # Business Settings
    b_settings = BusinessSettingsDocument(
        business_name="Elite Men's Wear",
        business_description="Premium fashion store",
        return_refund_policy="7-day returns for unused items",
        shipping_information="3-5 days delivery across India"
    )
    firebase_service.set_business_settings("tenant-test-biz", b_settings)
    yield
    firebase_service.clear_mock_data()


def test_01_product_lookup_from_firebase():
    """
    Test: Query products matching search terms from Firebase.
    """
    results = firebase_service.search_products(
        business_id="tenant-test-biz",
        query="cotton shirt",
        color="black"
    )
    assert len(results) == 1
    assert results[0].id == "prod-shirt-001"
    assert results[0].effective_price == 1299.0


def test_02_product_not_found_handling():
    """
    Test: When product is not found in Firebase, system responds with safe grounded message.
    """
    results = firebase_service.search_products(
        business_id="tenant-test-biz",
        query="Nike Air Jordan Shoes"
    )
    assert len(results) == 0

    val_res = validation_service.validate_and_sanitize_response(
        generated_reply="Yes we have Nike Air Jordan for ₹9,999 in stock!",
        verified_products=[],
        inventory_data={"found": False, "is_available": False},
        business_settings=None,
        customer_message="Do you have Nike Air Jordan Shoes?"
    )
    assert val_res.is_valid is False
    assert "don't have that information" in val_res.sanitized_text.lower() or "check with the business team" in val_res.sanitized_text.lower()


def test_03_invalid_size_handling():
    """
    Test: If customer requests size XXL when only S, M, L, XL are available,
    the response corrects the customer with valid sizes from Firebase.
    """
    inv = firebase_service.check_inventory(
        business_id="tenant-test-biz",
        product_id="prod-shirt-001",
        size="XXL"
    )
    assert inv["found"] is True
    assert "XXL" not in inv["available_sizes"]

    val_res = validation_service.validate_and_sanitize_response(
        generated_reply="Yes size XXL is available for this shirt!",
        verified_products=[{"name": "Formal Cotton Shirt", "price": 1499.0, "sale_price": 1299.0}],
        inventory_data=inv,
        business_settings=None,
        customer_message="Do you have size XXL?"
    )
    assert val_res.is_valid is False
    assert "XXL isn't available" in val_res.sanitized_text or "available sizes are" in val_res.sanitized_text


def test_04_invalid_color_handling():
    """
    Test: If customer requests yellow color when only black, blue, white are available.
    """
    inv = firebase_service.check_inventory(
        business_id="tenant-test-biz",
        product_id="prod-shirt-001",
        color="yellow"
    )
    assert inv["found"] is True
    assert "yellow" not in inv["available_colors"]

    val_res = validation_service.validate_and_sanitize_response(
        generated_reply="Yes, yellow is available for this shirt!",
        verified_products=[{"name": "Formal Cotton Shirt", "price": 1499.0, "sale_price": 1299.0}],
        inventory_data=inv,
        business_settings=None,
        customer_message="Do you have yellow shirt?"
    )
    assert val_res.is_valid is False
    assert "not available" in val_res.sanitized_text.lower()


def test_05_stock_availability_and_out_of_stock():
    """
    Test: Stock = 0 correctly identified as out of stock.
    """
    inv = firebase_service.check_inventory(
        business_id="tenant-test-biz",
        product_id="prod-blazer-002"
    )
    assert inv["found"] is True
    assert inv["is_available"] is False
    assert inv["available_quantity"] == 0

    val_res = validation_service.validate_and_sanitize_response(
        generated_reply="Yes, the blazer is in stock and available for you to buy!",
        verified_products=[{"name": "Navy Blue Blazer", "price": 4999.0, "sale_price": 3999.0}],
        inventory_data=inv,
        business_settings=None,
        customer_message="Can I buy the navy blue blazer?"
    )
    assert val_res.is_valid is False
    assert "out of stock" in val_res.sanitized_text.lower()


def test_06_exact_price_retrieval_and_unauthorized_discount_refusal():
    """
    Test: Verifies exact price (₹1,299) and rejects unauthorized discount request ('give for 800').
    """
    shirt = firebase_service.get_product("tenant-test-biz", "prod-shirt-001")
    assert shirt.effective_price == 1299.0

    val_res = validation_service.validate_and_sanitize_response(
        generated_reply="Sure, I can give it for 800 rupees today!",
        verified_products=[shirt.model_dump()],
        inventory_data={"found": True, "available_quantity": 27, "is_available": True},
        business_settings=None,
        customer_message="Can you give it for 800?"
    )
    assert val_res.is_valid is False
    assert "1,299" in val_res.sanitized_text or "1299" in val_res.sanitized_text
    assert "don't have" in val_res.sanitized_text.lower() or "current price" in val_res.sanitized_text.lower()


def test_07_gemini_hallucinated_price_detection():
    """
    Test: When LLM outputs a hallucinated price (₹1,499 instead of sale price ₹1,299),
    ValidationService catches the discrepancy and replaces it with the exact Firebase price.
    """
    shirt = firebase_service.get_product("tenant-test-biz", "prod-shirt-001")

    val_res = validation_service.validate_and_sanitize_response(
        generated_reply="The Formal Cotton Shirt is available for ₹1,499.00.",
        verified_products=[shirt.model_dump()],
        inventory_data={"found": True, "available_quantity": 27, "is_available": True},
        business_settings=None,
        customer_message="How much is this shirt?"
    )
    assert val_res.is_valid is False
    assert "Price mismatch" in val_res.violations[0]
    assert "₹1,299" in val_res.sanitized_text


def test_08_gemini_hallucinated_stock_detection():
    """
    Test: When LLM invents a stock number (50 in stock instead of 27),
    ValidationService detects and corrects the stock count.
    """
    inv = firebase_service.check_inventory("tenant-test-biz", "prod-shirt-001")

    val_res = validation_service.validate_and_sanitize_response(
        generated_reply="We currently have 50 in stock ready for dispatch.",
        verified_products=[],
        inventory_data=inv,
        business_settings=None,
        customer_message="How many are left?"
    )
    assert val_res.is_valid is False
    assert "Stock count mismatch" in val_res.violations[0]
    assert "27 in stock" in val_res.sanitized_text


def test_09_atomic_inventory_updates():
    """
    Test: Atomic inventory decrement prevents negative stock.
    """
    # Stock is 27
    success1 = firebase_service.atomic_update_inventory("tenant-test-biz", "prod-shirt-001", -20)
    assert success1 is True
    shirt_after = firebase_service.get_product("tenant-test-biz", "prod-shirt-001")
    assert shirt_after.available_quantity == 7

    # Attempt to order 10 when only 7 left
    success2 = firebase_service.atomic_update_inventory("tenant-test-biz", "prod-shirt-001", -10)
    assert success2 is False # Blocked to prevent negative stock!
    shirt_final = firebase_service.get_product("tenant-test-biz", "prod-shirt-001")
    assert shirt_final.available_quantity == 7


@pytest.mark.asyncio
async def test_10_whatsapp_outbound_handling(monkeypatch):
    """
    Test: WhatsApp send failure handling does not crash the system.
    """
    # Test valid call structure
    res = await WhatsAppService.send_whatsapp_message(
        phone_number_id="109876543210",
        to_number="+919876543210",
        text_body="Test outbound message",
        access_token="test_token"
    )
    assert "status_code" in res
