#!/usr/bin/env python3
"""
Starboyz Footwear — Interactive Terminal Chat
Direct conversational interface powered by Google Gemini and Cloud Firestore.
Natural human friend tone, consultative discovery, and in-chat checkout with COD and UPI QR.
"""

import os
import sys
import asyncio
import re
import random
import warnings
import logging
import contextlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

warnings.filterwarnings("ignore")
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("google.genai").setLevel(logging.ERROR)


@contextlib.contextmanager
def suppress_stderr():
    """Suppresses C-level and Python-level stderr warnings from third-party SDKs."""
    try:
        null_fd = os.open(os.devnull, os.O_RDWR)
        save_fd = os.dup(2)
        os.dup2(null_fd, 2)
        yield
    except Exception:
        yield
    finally:
        try:
            os.dup2(save_fd, 2)
            os.close(null_fd)
            os.close(save_fd)
        except Exception:
            pass


from app.config import settings
from app.services.firebase_service import firebase_service
from app.services.validation_service import validation_service
from app.services.gemini_service import gemini_service
from app.schemas.ai import GroundedResponseContext
from app.schemas.firebase_models import OrderDocument, OrderItemDocument

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


# Checkout State Tracker
checkout_session = {
    "active": False,
    "step": None,  # "collect_details" | "choose_payment" | "await_upi"
    "product": None,
    "size": "9",
    "price": 0.0,
    "mrp": 0.0,
    "customer_name": None,
    "delivery_address": None,
    "state_pincode": None,
    "payment_method": None,
}


def print_banner():
    width = 75
    print("\n" + "=" * width)
    print(f"{BOLD}{CYAN}{'STARBOYZ FOOTWEAR (TERMINAL CHAT)':^75}{RESET}")
    print("=" * width)
    print(f"{DIM}Store: {BOLD}Starboyz{RESET}{DIM} | AI Engine: {BOLD}Google Gemini ({settings.GEMINI_MODEL}){RESET}{DIM} | Cloud Firestore Grounded{RESET}")
    print(f"{DIM}Commands: Type naturally, {YELLOW}'checkout'{RESET}{DIM} to buy, {YELLOW}'catalog'{RESET}{DIM} for shoes, {YELLOW}'clear'{RESET}{DIM} to reset, {YELLOW}'exit'{RESET}{DIM} to quit.{RESET}\n")


def display_catalog():
    products = firebase_service.list_all_products("stridehub-shoes")
    print(f"\n{BOLD}{YELLOW}LIVE STARBOYZ SHOE CATALOG ({len(products)} Items):{RESET}")
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
        print(f" * {BOLD}{p.name:<30}{RESET} Rs. {p.price:,.0f} {DIM}(MRP Rs. {p.mrp:,.0f}){RESET} | Sizes: [{sizes_str}] | {stock_tag}")
    print("-" * 75 + "\n")


def print_upi_qr_code(amount: float, product_name: str, size: str):
    """Renders a clean UPI QR code in terminal for simulated scan and payment."""
    print(f"\n{BOLD}{PURPLE}==========================================================================={RESET}")
    print(f"{BOLD}{CYAN}{'SCAN UPI QR CODE TO COMPLETE PAYMENT (TEST MODE)':^75}{RESET}")
    print(f"{BOLD}{PURPLE}==========================================================================={RESET}")
    print(f"""
        {BOLD}┌────────────────────────────────────────┐{RESET}
        {BOLD}│  ██████████    ████  ██    ██████████  │{RESET}
        {BOLD}│  ██      ██    ████  ██    ██      ██  │{RESET}
        {BOLD}│  ██  ██  ██    ██    ██    ██  ██  ██  │{RESET}
        {BOLD}│  ██████████    ████████    ██████████  │{RESET}
        {BOLD}│                ██  ██                  │{RESET}
        {BOLD}│  ██████  ████████    ████████  ██████  │{RESET}
        {BOLD}│  ██  ██  ██    ██  ██    ██    ██      │{RESET}
        {BOLD}│  ██████████    ██  ██████████  ██████  │{RESET}
        {BOLD}│  ██      ██    ████  ██    ██      ██  │{RESET}
        {BOLD}│  ██  ██  ██    ██    ██    ██  ██  ██  │{RESET}
        {BOLD}│  ██████████    ████████    ██████████  │{RESET}
        {BOLD}└────────────────────────────────────────┘{RESET}
    """)
    print(f"  {BOLD}Item:{RESET}         {product_name} (UK Size {size})")
    print(f"  {BOLD}Amount:{RESET}       {GREEN}Rs. {amount:,.2f}{RESET} (Inclusive of all taxes and Free Shipping)")
    print(f"  {BOLD}UPI ID:{RESET}       {YELLOW}starboyz@okaxis{RESET} {DIM}(Starboyz Footwear Ltd){RESET}")
    print(f"  {BOLD}Supported:{RESET}    GPay, PhonePe, Paytm, BHIM, Cred UPI")
    print(f"{BOLD}{PURPLE}---------------------------------------------------------------------------{RESET}")
    print(f"  {BOLD}{YELLOW}Scan with your UPI app or type {GREEN}'PAID'{YELLOW} or {GREEN}'DONE'{YELLOW} to verify test payment.{RESET}")
    print(f"{BOLD}{PURPLE}===========================================================================\n{RESET}")


def detect_language_flavor(user_input: str, history: List[Dict[str, str]]) -> str:
    """Detects conversation language: 'tanglish', 'hinglish', 'tenglish', 'manglish', or 'english'."""
    all_text = " ".join([t.get("content", "") for t in history[-6:]] + [user_input]).lower()
    
    # Tamil / Tanglish triggers
    tanglish_words = [
        "venum", "sollunga", "iruka", "irukuma", "nalla", "kudunga", "panren", "panna",
        "machan", "thala", "epdi", "romba", "mattum", "edhuku", "enga", "kandippa",
        "seri", "aama", "illa", "annachi", "kudukureengala", "varuma", "podhum",
        "paravala", "naanum", "ungaluku", "tamil", "chennai", "coimbatore", "madurai", "vanakkam"
    ]
    if any(w in all_text for w in tanglish_words):
        return "tanglish"
        
    # Hindi / Hinglish triggers
    hinglish_words = [
        "chahiye", "kaise", "kya", "bhai", "batao", "dikhao", "dikhaye", "hoga",
        "milega", "kitna", "daam", "namaste", "haan", "nahi", "karo", "achha",
        "badhiya", "shukriya", "bhejo", "dedo", "karenge", "karna", "aap", "delhi", "mumbai"
    ]
    if any(w in all_text for w in hinglish_words):
        return "hinglish"

    # Telugu / Tenglish triggers
    tenglish_words = ["kavali", "cheppandi", "unda", "bhayya", "entha", "choodandi", "ivvandi"]
    if any(w in all_text for w in tenglish_words):
        return "tenglish"

    # Malayalam / Manglish triggers
    manglish_words = ["venam", "nokkunne", "para", "chetta", "vilayenta", "undo"]
    if any(w in all_text for w in manglish_words):
        return "manglish"

    return "english"


def handle_checkout_flow(user_input: str, history: List[Dict[str, str]]) -> Optional[str]:
    """
    Handles interactive step-by-step customer checkout with full language mirroring.
    """
    global checkout_session
    t = user_input.lower().strip()
    all_products = firebase_service.list_all_products("stridehub-shoes")
    lang = detect_language_flavor(user_input, history)

    # If checkout was just initiated
    if not checkout_session["active"]:
        target_prod = None
        for p in all_products:
            name_words = [w.lower() for w in p.name.split() if len(w) > 3]
            if any(w in t for w in name_words):
                target_prod = p
                break

        if not target_prod:
            for turn in reversed(history[-6:]):
                turn_text = turn.get("content", "").lower()
                for p in all_products:
                    name_words = [w.lower() for w in p.name.split() if len(w) > 3]
                    if any(w in turn_text for w in name_words):
                        target_prod = p
                        break
                if target_prod:
                    break

        if not target_prod:
            target_prod = all_products[0]

        size_match = re.search(r'(?:size\s*|uk\s*)(\d{1,2})', t)
        size_val = size_match.group(1) if size_match else "9"

        checkout_session["active"] = True
        checkout_session["step"] = "collect_details"
        checkout_session["product"] = target_prod
        checkout_session["size"] = size_val
        checkout_session["price"] = float(target_prod.price)
        checkout_session["mrp"] = float(target_prod.mrp)
        checkout_session["lang"] = lang

        if lang == "tanglish":
            return (
                f"Super choice bro! Ungaloda {target_prod.name} (UK Size {size_val}) order Rs. {target_prod.price:,.0f} ku free express delivery oda place pannidalam.\n\n"
                f"Unga delivery details anupunga bro:\n"
                f"1. Full Name\n"
                f"2. Full Address and City\n"
                f"3. State and Pincode\n\n"
                f"{DIM}(Orey message la anupalam, ex: 'Rishvanth, 42 100ft Road, Indiranagar, Bangalore, Karnataka - 560038'){RESET}"
            )
        elif lang == "hinglish":
            return (
                f"Badhiya choice bhai! Aapka {target_prod.name} (UK Size {size_val}) ka order Rs. {target_prod.price:,.0f} mein free express delivery ke sath place kar dete hain.\n\n"
                f"Apni delivery details bhej dijiye bhai:\n"
                f"1. Full Name\n"
                f"2. Full Address and City\n"
                f"3. State and Pincode\n\n"
                f"{DIM}(Ek hi message mein bhej sakte ho, ex: 'Rishvanth, 42 100ft Road, Indiranagar, Bangalore, Karnataka - 560038'){RESET}"
            )

        return (
            f"Great choice. Let's get your order placed for {target_prod.name} (UK Size {size_val}) for Rs. {target_prod.price:,.0f} with free express delivery.\n\n"
            f"Please send your delivery details:\n"
            f"1. Full Name\n"
            f"2. Full Address and City\n"
            f"3. State and Pincode\n\n"
            f"{DIM}(You can send it all in one message, like: 'Rishvanth, 42 100ft Road, Indiranagar, Bangalore, Karnataka - 560038'){RESET}"
        )

    # Step 1: Collect Details
    if checkout_session["step"] == "collect_details":
        checkout_session["delivery_address"] = user_input
        parts = [p.strip() for p in user_input.split(",") if p.strip()]
        checkout_session["customer_name"] = parts[0] if parts else "Customer"
        checkout_session["step"] = "choose_payment"

        prod = checkout_session["product"]
        size = checkout_session["size"]
        price = checkout_session["price"]
        mrp = checkout_session["mrp"]
        addr = checkout_session["delivery_address"]
        lang = checkout_session.get("lang", lang)

        if lang == "tanglish":
            return (
                f"Order Summary:\n"
                f"-----------------------------------------\n"
                f"Item:        {prod.name} (UK Size {size})\n"
                f"Price:       Rs. {price:,.0f} (MRP Rs. {mrp:,.0f})\n"
                f"Shipping:    Free Express Delivery (2-3 Days)\n"
                f"Total:       Rs. {price:,.0f}\n"
                f"Deliver To:  {addr}\n"
                f"-----------------------------------------\n\n"
                f"Payment epdi panna poreenga bro?\n"
                f"1. 'COD' nu type pannunga - Cash on Delivery (Delivery apo pay pannalam)\n"
                f"2. 'UPI' nu type pannunga - Instant UPI / QR Scan (GPay, PhonePe, Paytm)\n\n"
                f"Endha payment option ungaluku comfortable bro?"
            )
        elif lang == "hinglish":
            return (
                f"Order Summary:\n"
                f"-----------------------------------------\n"
                f"Item:        {prod.name} (UK Size {size})\n"
                f"Price:       Rs. {price:,.0f} (MRP Rs. {mrp:,.0f})\n"
                f"Shipping:    Free Express Delivery (2-3 Days)\n"
                f"Total:       Rs. {price:,.0f}\n"
                f"Deliver To:  {addr}\n"
                f"-----------------------------------------\n\n"
                f"Payment kaise karenge bhai?\n"
                f"1. 'COD' type karein - Cash on Delivery (Delivery ke time pay karein)\n"
                f"2. 'UPI' type karein - Instant UPI / QR Scan (GPay, PhonePe, Paytm)\n\n"
                f"Kaunsa payment option sahi rahega aapke liye?"
            )

        return (
            f"Order Summary:\n"
            f"-----------------------------------------\n"
            f"Item:        {prod.name} (UK Size {size})\n"
            f"Price:       Rs. {price:,.0f} (MRP Rs. {mrp:,.0f})\n"
            f"Shipping:    Free Express Delivery (2-3 Days)\n"
            f"Total:       Rs. {price:,.0f}\n"
            f"Deliver To:  {addr}\n"
            f"-----------------------------------------\n\n"
            f"How would you like to pay?\n"
            f"1. Type 'COD' for Cash on Delivery\n"
            f"2. Type 'UPI' for Instant UPI / QR Scan (GPay, PhonePe, Paytm)\n\n"
            f"Which payment option works best for you?"
        )

    # Step 2: Choose Payment
    if checkout_session["step"] == "choose_payment":
        lang = checkout_session.get("lang", lang)
        if "cod" in t or "cash" in t or "1" in t:
            checkout_session["payment_method"] = "Cash on Delivery"
            return finalize_order(is_cod=True, lang=lang)

        elif "upi" in t or "qr" in t or "gpay" in t or "phonepe" in t or "2" in t or "online" in t:
            checkout_session["payment_method"] = "UPI"
            checkout_session["step"] = "await_upi"
            prod = checkout_session["product"]
            print_upi_qr_code(checkout_session["price"], prod.name, checkout_session["size"])
            if lang == "tanglish":
                return f"Mela irukura QR code scan panni Rs. {checkout_session['price']:,.0f} UPI la pay pannidunga bro. Transfer pannadhuku appram 'PAID' illana 'DONE' nu type pannunga."
            elif lang == "hinglish":
                return f"Upar diye gaye QR code ko scan karke Rs. {checkout_session['price']:,.0f} UPI se pay karein. Payment hone ke baad 'PAID' ya 'DONE' reply karein."
            return "Please scan the QR code above to pay Rs. " + f"{checkout_session['price']:,.0f}" + " using any UPI app. Once done, type 'PAID' or 'DONE' to confirm."

    # Step 3: Await UPI Payment
    if checkout_session["step"] == "await_upi":
        lang = checkout_session.get("lang", lang)
        if any(w in t for w in ["paid", "done", "yes", "completed", "success", "sent", "transferred", "ok", "panniten", "ho gaya"]):
            return finalize_order(is_cod=False, lang=lang)
        else:
            if lang == "tanglish":
                return "Payment confirmation kaga wait panren bro. Transfer pannadhuku appram 'PAID' illana 'DONE' nu anupunga, illana Cash on Delivery ku 'COD' nu sollunga."
            elif lang == "hinglish":
                return "Payment confirmation ka wait kar rahe hain bhai. Transfer hone ke baad 'PAID' ya 'DONE' reply karein, ya Cash on Delivery ke liye 'COD' bolein."
            return "Waiting for payment confirmation. Please reply 'PAID' or 'DONE' once you have transferred, or reply 'COD' if you want Cash on Delivery instead."

    return None


def finalize_order(is_cod: bool, lang: str = "english") -> str:
    """Creates a verified OrderDocument in Cloud Firestore, decrements inventory atomically, and updates CRM."""
    global checkout_session
    prod = checkout_session["product"]
    size = checkout_session["size"]
    price = checkout_session["price"]
    name = checkout_session["customer_name"] or "Customer"
    addr = checkout_session["delivery_address"] or "Bangalore, Karnataka"
    pay_method = "Cash on Delivery" if is_cod else "UPI (Paid Online)"
    pay_status = "pending" if is_cod else "paid"
    cust_id = "+919876543210"

    # Generate unique Order ID and Tracking ID
    rand_id = random.randint(1000, 9999)
    order_id = f"SB-{rand_id}"
    tracking_id = f"BD{random.randint(100000, 999999)}IN"

    # Decrement inventory in Cloud Firestore atomically with audit movement
    try:
        firebase_service.atomic_update_inventory(
            business_id="stridehub-shoes",
            product_id=prod.id,
            quantity_delta=-1,
            reason="order_placed",
            reference_id=order_id,
            performed_by="terminal_chat"
        )
    except Exception:
        pass

    # Save order to Firestore
    order_doc = OrderDocument(
        order_id=order_id,
        businessId="stridehub-shoes",
        customer_id=cust_id,
        customer_name=name,
        contact_number=cust_id,
        lead_id=cust_id,
        product_id=prod.id,
        product_name=f"{prod.name} (UK Size {size})",
        quantity=1,
        amount=price,
        payment_method=pay_method,
        payment_status=pay_status,
        status="confirmed",
        delivery_address=addr,
        courier_partner="BlueDart Express",
        tracking_id=tracking_id,
        estimated_delivery="2-3 Business Days",
        order_date=datetime.now(timezone.utc).isoformat()
    )
    firebase_service.save_order("stridehub-shoes", order_doc)

    # Advance Lead State to Converted in CRM
    try:
        lead = firebase_service.get_lead_state("stridehub-shoes", cust_id)
        if lead:
            lead.stage = "converted"
            lead.qualification_score = 100.0
            lead.last_activity = datetime.now(timezone.utc).isoformat()
            firebase_service.save_lead_state("stridehub-shoes", cust_id, lead.model_dump())
    except Exception:
        pass

    # Reset checkout session
    checkout_session = {
        "active": False,
        "step": None,
        "product": None,
        "size": "9",
        "price": 0.0,
        "mrp": 0.0,
        "customer_name": None,
        "delivery_address": None,
        "state_pincode": None,
        "payment_method": None,
        "lang": "english",
    }

    status_badge = "PENDING (Pay on delivery)" if is_cod else "PAID (UPI Verified)"

    if lang == "tanglish":
        return (
            f"Unga order confirm aayiduchu bro!\n\n"
            f"-----------------------------------------\n"
            f"Order ID:     #{order_id}\n"
            f"Shoe:         {prod.name} (UK Size {size})\n"
            f"Total:        Rs. {price:,.0f} ({status_badge})\n"
            f"Courier:      BlueDart Express (AWB: {tracking_id})\n"
            f"Delivery:     2 to 3 Business Days kula door delivery aayidum\n"
            f"Address:      {addr}\n"
            f"-----------------------------------------\n\n"
            f"Unga order system la register aayiduchu. Status check panna eppo venalum 'track #{order_id}' nu type pannunga. Starboyz la shop pannadhuku romba thanks bro!"
        )
    elif lang == "hinglish":
        return (
            f"Aapka order confirm ho gaya hai bhai!\n\n"
            f"-----------------------------------------\n"
            f"Order ID:     #{order_id}\n"
            f"Shoe:         {prod.name} (UK Size {size})\n"
            f"Total:        Rs. {price:,.0f} ({status_badge})\n"
            f"Courier:      BlueDart Express (AWB: {tracking_id})\n"
            f"Delivery:     2 se 3 Business Days mein deliver ho jayega\n"
            f"Address:      {addr}\n"
            f"-----------------------------------------\n\n"
            f"Aapka order hamare system mein book ho gaya hai. Status check karne ke liye 'track #{order_id}' type karein. Starboyz se shopping karne ke liye shukriya bhai!"
        )

    return (
        f"Your order has been confirmed!\n\n"
        f"-----------------------------------------\n"
        f"Order ID:     #{order_id}\n"
        f"Shoe:         {prod.name} (UK Size {size})\n"
        f"Total:        Rs. {price:,.0f} ({status_badge})\n"
        f"Courier:      BlueDart Express (AWB: {tracking_id})\n"
        f"Delivery:     Expected within 2 to 3 Business Days\n"
        f"Address:      {addr}\n"
        f"-----------------------------------------\n\n"
        f"We have registered your order in our system. You can track this anytime by typing 'track #{order_id}'. Thank you for shopping with Starboyz!"
    )


def strip_emojis(text: str) -> str:
    """Removes emojis and emoticons from text."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA00-\U0001FA6F"  # chess symbols, etc.
        "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
        "\U00002600-\U000026FF"  # miscellaneous symbols
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text).strip()


def process_message(
    user_input: str,
    history: List[Dict[str, str]],
    business_id: str = "stridehub-shoes"
) -> Dict[str, Any]:
    """
    Processes a customer message using Firestore grounding and Gemini,
    and synchronizes CRM leads, qualification scores, and conversation messages.
    """
    global checkout_session
    customer_id = "+919876543210"

    # Synchronize Customer Record
    try:
        firebase_service.get_or_create_customer(business_id, customer_id, name="Customer")
    except Exception:
        pass

    # Record Customer Message in Firestore
    try:
        firebase_service.record_conversation_message(business_id, customer_id, "user", user_input)
    except Exception:
        pass

    # Check for checkout flow triggers
    checkout_triggers = ["checkout", "buy", "order this", "place order", "i want to buy", "book this", "purchase", "confirm order"]
    if checkout_session["active"] or any(trig in user_input.lower() for trig in checkout_triggers):
        checkout_reply = handle_checkout_flow(user_input, history)
        if checkout_reply:
            cleaned_rep = strip_emojis(checkout_reply)
            try:
                firebase_service.record_conversation_message(business_id, customer_id, "assistant", cleaned_rep)
            except Exception:
                pass
            return {
                "reply_text": cleaned_rep,
                "matched_products": [],
                "order_info": None
            }

    # 1. Extract intent & signals
    sales_info = gemini_service.extract_sales_signals(user_input, history)
    query_text = sales_info.product_query or user_input

    # 2. Check for order tracking
    order_info = None
    order_match = re.search(r'#?(SH-\d{4}|SV-\d{4}|SB-\d{4}|\d{4})', user_input, re.IGNORECASE)
    if ("order" in user_input.lower() or "track" in user_input.lower() or "status" in user_input.lower()) and order_match:
        ord_id = order_match.group(1).upper()
        if not ord_id.startswith(("SH-", "SV-", "SB-")):
            ord_id = f"SB-{ord_id}"
        found_order = firebase_service.get_order(business_id, ord_id)
        if not found_order and ord_id.startswith("SB-"):
            found_order = firebase_service.get_order(business_id, ord_id.replace("SB-", "SH-"))
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
        "shipping": getattr(b_settings, "shipping_information", "Free standard delivery across India on orders above Rs. 999."),
        "returns": getattr(b_settings, "return_refund_policy", "7-day hassle-free return policy for unworn shoes."),
        "exchange": getattr(b_settings, "exchange_policy", "15-day free size exchange available."),
        "payment": ", ".join(getattr(b_settings, "payment_methods", ["UPI", "Card", "COD"])),
        "working_hours": getattr(b_settings, "working_hours", "9:00 AM - 9:00 PM"),
        "address": getattr(b_settings, "address", "Starboyz Flagship Store, Bengaluru")
    }

    # 4. Synchronize Lead State & Scoring in CRM
    try:
        score_need = 30.0 if bool(sales_info.product_query or matched_products) else 10.0
        score_budget = 40.0 if sales_info.budget else 0.0
        score_timeline = 30.0 if sales_info.timeline else 0.0
        tot_score = min(100.0, score_need + score_budget + score_timeline)

        target_stage = "enquired"
        if tot_score >= 70.0 and sales_info.budget:
            target_stage = "quoted"
        elif sales_info.budget or sales_info.timeline:
            target_stage = "engaged"

        matched_p_ids = [p.id for p in matched_products[:3]]
        matched_p_names = [p.name for p in matched_products[:3]]

        lead_data = {
            "lead_id": customer_id,
            "businessId": business_id,
            "customer_id": customer_id,
            "contact_number": customer_id,
            "name": "Customer",
            "stage": target_stage,
            "qualification_score": tot_score,
            "score_breakdown": {"need": score_need, "budget": score_budget, "timeline": score_timeline, "engagement": tot_score},
            "budget_signal": f"Rs. {sales_info.budget:,.0f}" if sales_info.budget else None,
            "timeline_signal": sales_info.timeline,
            "need_summary": query_text,
            "interested_products": matched_p_ids,
            "interested_product_names": matched_p_names,
            "last_interaction": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat()
        }
        firebase_service.save_lead_state(business_id, customer_id, lead_data)
    except Exception as e:
        logger.warning(f"Note: CRM lead sync notice: {e}")

    # 5. Build Grounded Context
    context = GroundedResponseContext(
        business_name="Starboyz",
        business_description="Starboyz Footwear - Style, Performance and Comfort",
        current_stage="inquiry",
        lead_name="Customer",
        conversation_history=history,
        customer_message=user_input,
        matched_products=[p.model_dump() for p in matched_products[:3]],
        verified_products=verified_catalog,
        inventory_data=inventory_map,
        business_policies=policies_dict
    )

    # 6. Generate AI Response with suppressed third-party stderr warnings
    with suppress_stderr():
        reply_text = gemini_service.generate_conversational_response(context)

    # 7. Validate anti-hallucination
    validation_res = validation_service.validate_and_sanitize_response(
        generated_reply=reply_text,
        verified_products=verified_catalog,
        inventory_data=inventory_map,
        business_settings=b_settings,
        customer_message=user_input
    )

    final_reply = strip_emojis(validation_res.sanitized_text or reply_text)

    # Record Assistant Message in Firestore
    try:
        firebase_service.record_conversation_message(business_id, customer_id, "assistant", final_reply)
    except Exception:
        pass

    # Show product recommendation cards ONLY when customer specifies budget/size or asks about a specific shoe
    is_specific_query = any(
        kw in user_input.lower()
        for kw in ["stride", "mountain", "nitro", "zoom", "glide", "oxford", "volt", "recommend", "show me", "options under", "size"]
    ) and bool(matched_products)

    return {
        "reply_text": final_reply,
        "matched_products": [p.model_dump() for p in matched_products[:2]] if is_specific_query else [],
        "order_info": order_info,
        "sales_info": sales_info
    }


def main():
    print_banner()
    history: List[Dict[str, str]] = []

    print(f"{BOLD}{GREEN}Starboyz:{RESET} Hey! Welcome to Starboyz. How can I help you find the right pair of shoes today?\n")

    while True:
        try:
            user_msg = input(f"{BOLD}{BLUE}You:{RESET} ").strip()
            if not user_msg:
                continue

            if user_msg.lower() in ["exit", "quit", "q", ":q"]:
                print(f"\n{BOLD}{CYAN}Thanks for stopping by Starboyz. Have a good one!{RESET}\n")
                break

            if user_msg.lower() == "catalog":
                display_catalog()
                continue

            if user_msg.lower() == "clear":
                history.clear()
                print(f"\n{YELLOW}Conversation history cleared.{RESET}\n")
                continue

            # Process AI conversation
            result = process_message(user_msg, history)
            reply = result["reply_text"]

            # Display Agent Response
            print(f"\n{BOLD}{GREEN}Starboyz:{RESET}\n{reply}")

            # Display Product Cards if relevant products matched
            if result.get("matched_products"):
                print(f"\n  {CYAN}Available Matching Shoes:{RESET}")
                for p in result["matched_products"]:
                    sizes = p.get('availableSizes') or p.get('sizes') or [5, 6, 7, 8, 9, 10, 11, 12]
                    sizes_str = ", ".join(map(str, sizes))
                    p_name = p.get('name', 'Product')
                    p_price = float(p.get('price') or p.get('salePrice') or 0.0)
                    p_mrp = float(p.get('mrp') or p.get('mrpPrice') or p_price * 1.25)
                    p_stock = int(p.get('quantity') or p.get('stock') or 0)
                    print(f"     * {BOLD}{p_name}{RESET} | {GREEN}Rs. {p_price:,.0f}{RESET} {DIM}(MRP Rs. {p_mrp:,.0f}){RESET} | Sizes: [{sizes_str}] | Stock: {p_stock} left")

            # Display Order Card if order was tracked
            if result.get("order_info"):
                card = result["order_info"]
                ord_num = card.get('order_id') or card.get('orderId') or 'SH-8942'
                trk_num = card.get('tracking_id') or card.get('trackingNumber') or 'BD982341IN'
                stat = card.get('status', 'DISPATCHED')
                print(f"\n  {CYAN}Live Order Tracking:{RESET} #{ord_num} | Status: {BOLD}{str(stat).upper()}{RESET} | Courier: BlueDart ({trk_num})")

            print()

            # Append to history
            history.append({"role": "user", "content": user_msg})
            history.append({"role": "assistant", "content": reply})

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{BOLD}{CYAN}Thanks for chatting with Starboyz. Goodbye!{RESET}\n")
            break


if __name__ == "__main__":
    main()
