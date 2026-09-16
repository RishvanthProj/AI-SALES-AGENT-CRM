#!/usr/bin/env python3
"""
StrideHub Shoes — Interactive Terminal AI Sales Agent
Direct conversational interface powered by Google Gemini and Cloud Firestore.
"""

import sys
import asyncio
import re
import warnings
import logging
from typing import List, Dict, Any

warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="google")
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)

from app.config import settings
from app.services.firebase_service import firebase_service
from app.services.validation_service import validation_service
from app.services.gemini_service import gemini_service
from app.schemas.ai import GroundedResponseContext

# Terminal Colors & Styling
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
PURPLE = "\033[95m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
RESET = "\033[0m"


def print_banner():
    width = 75
    print("\n" + "=" * width)
    print(f"{BOLD}{CYAN}{'👟 STRIDEHUB SHOES — AI SALES ASSISTANT (TERMINAL CHAT)':^75}{RESET}")
    print("=" * width)
    print(f"{DIM}AI Provider: {BOLD}Google Gemini ({settings.GEMINI_MODEL}){RESET}{DIM} | Database: {BOLD}Cloud Firestore{RESET}")
    print(f"{DIM}Commands: Type your message, {YELLOW}'catalog'{RESET}{DIM} to see shoes, {YELLOW}'clear'{RESET}{DIM} to reset, {YELLOW}'exit'{RESET}{DIM} to quit.{RESET}\n")


def display_catalog():
    products = firebase_service.list_all_products("stridehub-shoes")
    print(f"\n{BOLD}{YELLOW}📦 LIVE FIRESTORE SHOE CATALOG ({len(products)} Items):{RESET}")
    print("-" * 75)
    for p in products:
        stock_qty = p.quantity
        if stock_qty > 5:
            stock_tag = f"{GREEN}In Stock ({stock_qty}){RESET}"
        elif stock_qty > 0:
            stock_tag = f"{YELLOW}Low Stock ({stock_qty}){RESET}"
        else:
            stock_tag = f"{RED}Out of Stock (0){RESET}"

        sizes_str = ", ".join(map(str, p.availableSizes)) if p.availableSizes else "5-12"
        print(f" • {BOLD}{p.name:<30}{RESET} ₹{p.price:,.0f} {DIM}(MRP ₹{p.mrp:,.0f}){RESET} | Sizes: [{sizes_str}] | {stock_tag}")
    print("-" * 75 + "\n")


def process_message(
    user_input: str,
    history: List[Dict[str, str]],
    business_id: str = "stridehub-shoes"
) -> Dict[str, Any]:
    """
    Processes a customer message using Firestore grounding and Gemini.
    """
    # 1. Extract intent & signals
    sales_info = gemini_service.extract_sales_signals(user_input, history)
    query_text = sales_info.product_query or user_input

    # 2. Check for order tracking
    order_info = None
    order_match = re.search(r'#?(SH-\d{4}|SV-\d{4}|\d{4})', user_input, re.IGNORECASE)
    if ("order" in user_input.lower() or "track" in user_input.lower() or "status" in user_input.lower()) and order_match:
        ord_id = order_match.group(1).upper()
        if not ord_id.startswith(("SH-", "SV-")):
            ord_id = f"SH-{ord_id}"
        found_order = firebase_service.get_order(business_id, ord_id)
        if found_order:
            order_info = found_order.model_dump()

    # 3. Match products in Firestore
    matched_products = firebase_service.search_products(
        business_id=business_id,
        query=query_text,
        max_budget=sales_info.budget,
        color=sales_info.color,
        size=sales_info.size
    )

    if not matched_products and any(cat in user_input.lower() for cat in ["running", "casual", "formal", "trail", "sneaker", "walking", "jogging", "gym"]):
        for cat in ["running", "casual", "formal", "trail", "sneaker", "walking", "jogging", "gym"]:
            if cat in user_input.lower():
                matched_products = firebase_service.search_products(business_id=business_id, query=cat)
                if matched_products:
                    break

    all_prods = firebase_service.list_all_products(business_id)
    verified_catalog = [p.model_dump() for p in all_prods]
    inventory_map = {p.id: p.quantity for p in all_prods}
    b_settings = firebase_service.get_business_settings(business_id)
    policies_dict = {
        "shipping": getattr(b_settings, "shipping_information", "Free standard delivery across India on orders above ₹999."),
        "returns": getattr(b_settings, "return_refund_policy", "7-day hassle-free return policy for unworn shoes."),
        "exchange": getattr(b_settings, "exchange_policy", "15-day free size exchange available."),
        "payment": ", ".join(getattr(b_settings, "payment_methods", ["UPI", "Card", "COD"])),
        "working_hours": getattr(b_settings, "working_hours", "9:00 AM - 9:00 PM"),
        "address": getattr(b_settings, "address", "StrideHub Flagship Store, Bengaluru")
    }

    # 4. Build Grounded Context
    context = GroundedResponseContext(
        business_name=b_settings.business_name,
        business_description=b_settings.business_description,
        current_stage="inquiry",
        lead_name="Customer",
        conversation_history=history,
        customer_message=user_input,
        matched_products=[p.model_dump() for p in matched_products[:3]],
        verified_products=verified_catalog,
        inventory_data=inventory_map,
        business_policies=policies_dict
    )

    # 5. Generate AI Response
    reply_text = gemini_service.generate_conversational_response(context)

    # 6. Validate anti-hallucination
    validation_res = validation_service.validate_and_sanitize_response(
        generated_reply=reply_text,
        verified_products=verified_catalog,
        inventory_data=inventory_map,
        business_settings=b_settings,
        customer_message=user_input
    )

    final_reply = validation_res.sanitized_text or reply_text

    return {
        "reply_text": final_reply,
        "matched_products": [p.model_dump() for p in matched_products[:2]],
        "order_info": order_info
    }


def main():
    print_banner()
    history: List[Dict[str, str]] = []

    print(f"{BOLD}{GREEN}🤖 StrideHub AI:{RESET} Hello there! 👋 Welcome to StrideHub Shoes. How can I help you find your perfect pair today? 👟\n")

    while True:
        try:
            user_msg = input(f"{BOLD}{BLUE}👤 You:{RESET} ").strip()
            if not user_msg:
                continue

            if user_msg.lower() in ["exit", "quit", "q", ":q"]:
                print(f"\n{BOLD}{CYAN}👟 Thanks for visiting StrideHub Shoes! Have a wonderful day! 👋{RESET}\n")
                break

            if user_msg.lower() == "catalog":
                display_catalog()
                continue

            if user_msg.lower() == "clear":
                history.clear()
                print(f"\n{YELLOW}🧹 Conversation history reset.{RESET}\n")
                continue

            # Process AI conversation
            result = process_message(user_msg, history)
            reply = result["reply_text"]

            # Display Agent Response
            print(f"\n{BOLD}{GREEN}🤖 StrideHub AI:{RESET} {reply}")

            # Display Product Cards if any matched
            if result.get("matched_products"):
                print(f"\n  {CYAN}📦 Recommended Products:{RESET}")
                for p in result["matched_products"]:
                    sizes = p.get('availableSizes') or p.get('sizes') or [5, 6, 7, 8, 9, 10, 11, 12]
                    sizes_str = ", ".join(map(str, sizes))
                    print(f"     • {BOLD}{p.get('name')}{RESET} | {GREEN}₹{p.get('price', 0):,.0f}{RESET} {DIM}(MRP ₹{p.mrp:,.0f}){RESET} | Sizes: [{sizes_str}] | Stock: {p.get('quantity', 0)} left")

            # Display Order Card if order was tracked
            if result.get("order_info"):
                card = result["order_info"]
                ord_num = card.get('order_id') or card.get('orderId') or 'SH-8942'
                trk_num = card.get('tracking_id') or card.get('trackingNumber') or 'BD982341IN'
                stat = card.get('status', 'DISPATCHED')
                print(f"\n  {CYAN}🚚 Live Order Status Card:{RESET} #{ord_num} | Status: {BOLD}{str(stat).upper()}{RESET} | Courier: BlueDart ({trk_num})")

            print()

            # Append to history
            history.append({"role": "user", "content": user_msg})
            history.append({"role": "assistant", "content": reply})

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{BOLD}{CYAN}👟 Thanks for chatting with StrideHub Shoes! Goodbye! 👋{RESET}\n")
            break


if __name__ == "__main__":
    main()
