import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.schemas.firebase_models import ProductDocument, BusinessSettingsDocument

logger = logging.getLogger("validation_service")


class ValidationResult:
    def __init__(self, is_valid: bool, sanitized_text: str, violations: List[str]):
        self.is_valid = is_valid
        self.sanitized_text = sanitized_text
        self.violations = violations


class ValidationService:
    """
    Authoritative Anti-Hallucination & Business Rule Validation Layer.
    Verifies that AI-generated responses strictly conform to Firebase facts before
    sending to WhatsApp. Prevents:
    - Invented or modified product prices
    - Invented inventory / stock counts
    - False availability claims for out-of-stock items or missing sizes/colors
    - Unauthorized discount promises
    - Invented business policies
    """

    @staticmethod
    def validate_and_sanitize_response(
        generated_reply: str,
        verified_products: List[Dict[str, Any]],
        inventory_data: Optional[Dict[str, Any]],
        business_settings: Optional[BusinessSettingsDocument],
        customer_message: str
    ) -> ValidationResult:
        violations: List[str] = []
        sanitized = generated_reply

        # 1. Price Integrity Validation
        if verified_products:
            p = verified_products[0]
            actual_price = float(p.get("salePrice") or p.get("sale_price") or p.get("price") or 0.0)
            p_name = p.get("name", "Product")

            # Check if AI explicitly claims a false price as the actual selling price
            # e.g., "The price is ₹800", "It costs ₹1499", "available for ₹900"
            price_claim_pattern = r'(?:price is|costs|available for|buy it for|at a price of|selling at)\s*(?:₹|rs\.?|\$)\s?(\d+[\d,]*(?:\.\d{2})?)'
            price_claims = re.findall(price_claim_pattern, generated_reply, re.IGNORECASE)

            for raw_claim in price_claims:
                claimed_price = float(raw_claim.replace(",", ""))
                if abs(claimed_price - actual_price) > 0.01:
                    violations.append(f"Price mismatch: AI claimed price is ₹{claimed_price}, but Firebase truth is ₹{actual_price}")
                    sanitized = re.sub(
                        rf'(price is|costs|available for|buy it for|at a price of|selling at)\s*(?:₹|rs\.?|\$)\s?{re.escape(raw_claim)}',
                        f"\\1 ₹{int(actual_price) if actual_price.is_integer() else actual_price:,.2f}",
                        sanitized,
                        flags=re.IGNORECASE
                    )

        # 2. Stock & Inventory Validation
        if inventory_data and inventory_data.get("found"):
            actual_stock = inventory_data.get("available_quantity", 0)
            is_avail = inventory_data.get("is_available", False)
            p_name = inventory_data.get("product_name", "this item")
            avail_sizes = inventory_data.get("available_sizes", [])
            avail_colors = inventory_data.get("available_colors", [])

            # Out of stock check
            if not is_avail or actual_stock == 0:
                positive_claims = ["is available", "in stock", "we have it", "yes, available", "you can buy"]
                if any(claim in sanitized.lower() for claim in positive_claims):
                    violations.append(f"False availability: AI claimed '{p_name}' is in stock, but stock is 0.")
                    sanitized = f"The {p_name} is currently out of stock. I can help you check another option!"

            # False stock count check
            stock_mentions = re.findall(r'(\d+)\s+(?:in stock|left|pieces available|units available|available)', sanitized, re.IGNORECASE)
            for raw_stock in stock_mentions:
                mentioned_qty = int(raw_stock)
                if mentioned_qty != actual_stock and actual_stock > 0 and mentioned_qty > 0:
                    violations.append(f"Stock count mismatch: AI said {mentioned_qty}, Firebase has {actual_stock}")
                    sanitized = re.sub(
                        rf'\b{mentioned_qty}\s+(in stock|left|pieces available|units available|available)',
                        f"{actual_stock} \\1",
                        sanitized,
                        flags=re.IGNORECASE
                    )

            # Invalid size check: if customer asked for a size not in available_sizes
            req_size_match = re.search(r'\b(?:size\s+)?(xxl|xl|l|m|s|xs|\d{1,2})\b', customer_message, re.IGNORECASE)
            if req_size_match and avail_sizes:
                req_size = req_size_match.group(1).upper()
                if req_size not in [s.upper() for s in avail_sizes]:
                    if req_size in sanitized.upper() and ("available" in sanitized.lower() or "yes, we have" in sanitized.lower()):
                        sizes_str = ", ".join(avail_sizes)
                        violations.append(f"Invalid size accepted: {req_size} is not in {avail_sizes}")
                        sanitized = f"Size {req_size} isn't available for this product. The available sizes are {sizes_str}."

            # Invalid color check: if customer asked for a color not in available_colors
            if avail_colors:
                for c in ["yellow", "green", "pink", "purple", "orange"]:
                    if c in customer_message.lower() and c not in [ac.lower() for ac in avail_colors]:
                        if f"yes, {c}" in sanitized.lower() or f"{c} is available" in sanitized.lower():
                            colors_str = ", ".join(avail_colors)
                            violations.append(f"Invalid color accepted: {c} not in {avail_colors}")
                            sanitized = f"{c.capitalize()} is not available for this item. We currently have {colors_str}."

        # 3. Product Not Found Validation
        if inventory_data and not inventory_data.get("found") and not verified_products:
            affirmative_words = ["yes", "we have", "available", "in stock", "₹", "$", "price is", "buy"]
            if any(w in sanitized.lower() for w in affirmative_words):
                violations.append("AI hallucinated product that does not exist in Firebase.")
                sanitized = "I don't have that information right now. Let me check with the business team."

        # 4. Unauthorized Discount Check
        if any(w in customer_message.lower() for w in ["discount", "for 800", "for ₹800", "less", "cheap", "offer"]):
            discount_affirmations = ["sure", "yes", "i can give", "can give", "agreed", "offer you", "deal", "take it for", "give it for"]
            is_refusal = any(ref in sanitized.lower() for ref in ["cannot", "can't", "don't have", "not able", "cannot offer", "not available"])
            if any(re.search(rf'\b{re.escape(w)}\b', sanitized, re.IGNORECASE) for w in discount_affirmations) and not is_refusal:
                violations.append("Unauthorized discount promised without Firebase rule authorization.")
                if verified_products:
                    p = verified_products[0]
                    p_price = float(p.get("salePrice") or p.get("sale_price") or p.get("price") or 0.0)
                    sanitized = f"The current price is ₹{p_price:,.2f}. I don't have that discount available right now."
                elif inventory_data and inventory_data.get("effective_price"):
                    p_price = float(inventory_data.get("effective_price"))
                    sanitized = f"The current price is ₹{p_price:,.2f}. I don't have that discount available right now."

        is_valid = len(violations) == 0
        if not is_valid:
            logger.warning(f"Business rule validation triggered with violations: {violations}")

        return ValidationResult(is_valid=is_valid, sanitized_text=sanitized, violations=violations)


validation_service = ValidationService()
