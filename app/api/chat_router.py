import re
import uuid
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.firebase_service import firebase_service
from app.services.validation_service import validation_service
from app.services.ai_service_factory import get_ai_provider
from app.schemas.ai import GroundedResponseContext
from app.agent.graph import sales_graph
from app.agent.state import SalesAgentState

logger = logging.getLogger("chat_router")
router = APIRouter(prefix="/api/chat", tags=["Web Chat"])


class ChatMessageRequest(BaseModel):
    message: str
    phone_number: str = "+919876543210"
    customer_name: Optional[str] = "Customer"
    business_id: str = "stridehub-shoes"


class ChatMessageResponse(BaseModel):
    reply_text: str
    stage: str
    qualification_score: float
    matched_products: List[Dict[str, Any]] = []
    inventory_data: Optional[Dict[str, Any]] = None
    order_info: Optional[Dict[str, Any]] = None
    quick_replies: List[str] = []
    route_destination: Optional[str] = None


@router.post("", response_model=ChatMessageResponse)
@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(payload: ChatMessageRequest):
    """
    Processes customer chat messages with Google Gemini & Firebase Firestore Grounding:
    1. Extracts intent & sales entities using Gemini.
    2. Queries Firestore as the single source of truth (products, inventory, orders, policies).
    3. Runs LangGraph state machine for qualification & scoring.
    4. Generates natural conversational AI response using Gemini.
    5. Validates & sanitizes copy against Firebase facts.
    6. Syncs customer state to Firestore and returns rich product/order payloads.
    """
    business_id = payload.business_id or "stridehub-shoes"
    phone_number = payload.phone_number or "+919876543210"
    message_text = payload.message.strip()

    if not message_text:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    ai = get_ai_provider()
    b_settings = firebase_service.get_business_settings(business_id)

    # 1. Look up / create customer in Firebase
    customer = firebase_service.get_or_create_customer(
        business_id=business_id,
        phone_number=phone_number,
        name=payload.customer_name
    )

    # Record user message in Firestore
    firebase_service.record_conversation_message(
        business_id=business_id,
        customer_id=customer.id,
        role="user",
        content=message_text
    )

    # 2. Get recent conversation history for memory
    history = firebase_service.get_recent_conversation_history(
        business_id=business_id,
        customer_id=customer.id,
        limit=6
    )

    # 3. Check for Order Lookup intent
    order_info = None
    order_match = re.search(r'#?(SH-\d{4}|SV-\d{4}|\d{4})', message_text, re.IGNORECASE)
    if ("order" in message_text.lower() or "track" in message_text.lower() or "status" in message_text.lower()) and order_match:
        ord_id = order_match.group(1).upper()
        if not ord_id.startswith(("SH-", "SV-")):
            ord_id = f"SH-{ord_id}"
        found_order = firebase_service.get_order(business_id, ord_id)
        if found_order:
            order_info = found_order.model_dump()

    # 4. Search authentic products in Firebase
    sales_info = ai.extract_sales_signals(message_text, history)
    query_text = sales_info.product_query or message_text

    matched_products = firebase_service.search_products(
        business_id=business_id,
        query=query_text,
        max_budget=sales_info.budget,
        color=sales_info.color,
        size=sales_info.size
    )

    # If no specific search match, check if general shoe category mentioned
    if not matched_products and any(cat in message_text.lower() for cat in ["running", "casual", "formal", "trail", "sneaker", "walking", "jogging"]):
        for cat in ["running", "casual", "formal", "trail", "sneaker", "walking", "jogging"]:
            if cat in message_text.lower():
                matched_products = firebase_service.search_products(business_id=business_id, query=cat)
                break

    # If user asked for products under a budget
    if not matched_products and sales_info.budget:
        matched_products = firebase_service.search_products(
            business_id=business_id,
            query="",
            max_budget=sales_info.budget
        )

    # If still empty, get all top shoes so AI has live context
    if not matched_products:
        matched_products = firebase_service.list_all_products(business_id)

    verified_prods = [p.model_dump(by_alias=True) for p in matched_products]

    inventory_data = None
    if matched_products:
        inventory_data = firebase_service.check_inventory(
            business_id=business_id,
            product_id=matched_products[0].id,
            size=sales_info.size,
            color=sales_info.color
        )

    # 5. Prepare and Execute LangGraph State Machine for qualification
    lead_state = firebase_service.get_lead_state(business_id, customer.id)
    curr_stage = lead_state.stage if lead_state else "greet"
    curr_score = float(lead_state.qualification_score if lead_state else 0.0)

    initial_state: SalesAgentState = {
        "tenant_id": business_id,
        "lead_id": customer.id,
        "contact_number": phone_number,
        "lead_name": customer.name or payload.customer_name,
        "current_stage": curr_stage,
        "incoming_message": message_text,
        "need_summary": (lead_state.need_summary if lead_state else None) or query_text,
        "budget_signal": (lead_state.budget_signal if lead_state else None) or sales_info.budget_range,
        "timeline_signal": (lead_state.timeline_signal if lead_state else None) or sales_info.timeline,
        "qualification_score": curr_score,
        "route_destination": lead_state.route_destination if lead_state else None,
        "reply_text": "",
        "history": history,
        "verified_products": verified_prods,
        "inventory_data": inventory_data,
        "is_inappropriate": sales_info.inappropriate_content,
        "is_jailbreak": sales_info.is_jailbreak_attempt
    }

    final_state = sales_graph.invoke(initial_state)
    final_stage = final_state.get("current_stage", "qualify")
    final_score = float(final_state.get("qualification_score", 0.0))
    final_route = final_state.get("route_destination")

    # 6. Generate Conversational AI Response strictly grounded in Firestore
    context = GroundedResponseContext(
        business_name=b_settings.business_name,
        business_description=b_settings.business_description,
        current_stage=final_stage,
        lead_name=customer.name or payload.customer_name,
        conversation_history=history,
        verified_products=verified_prods[:4],
        inventory_data=inventory_data,
        business_policies={
            "shipping": b_settings.shipping_information,
            "return_policy": b_settings.return_refund_policy,
            "exchange_policy": b_settings.exchange_policy,
            "payment_methods": b_settings.payment_methods,
            "working_hours": b_settings.working_hours
        },
        customer_message=message_text,
        known_signals={
            "intent": sales_info.intent,
            "need": query_text,
            "budget": sales_info.budget_range or sales_info.budget,
            "size": sales_info.size,
            "color": sales_info.color,
            "timeline": sales_info.timeline,
            "qualification_score": final_score
        }
    )

    raw_reply = ai.generate_conversational_response(context)

    # 7. Validate & Sanitize against Firebase Anti-Hallucination rules
    val_res = validation_service.validate_and_sanitize_response(
        generated_reply=raw_reply,
        verified_products=verified_prods[:4],
        inventory_data=inventory_data,
        business_settings=b_settings,
        customer_message=message_text
    )
    reply_text = val_res.sanitized_text

    # If order tracking info was found, format clean tracking message
    if order_info:
        ord_num = order_info.get("order_id") or order_info.get("orderNumber", "SH-8942")
        prod_nm = order_info.get("product_name", "Shoes")
        stat = str(order_info.get("status", "dispatched")).upper()
        cour = order_info.get("courier_partner") or order_info.get("courier_name", "BlueDart Express")
        trkid = order_info.get("tracking_id") or order_info.get("tracking_number", "BD982341IN")
        est = order_info.get("estimated_delivery", "Tomorrow by 4:00 PM")
        reply_text = f"Order #{ord_num} ({prod_nm}) is currently {stat}. Courier: {cour} (Tracking: {trkid}). Estimated delivery: {est}."

    # 8. Save updated lead state & assistant reply in Firestore
    firebase_service.save_lead_state(
        business_id=business_id,
        lead_id=customer.id,
        lead_data={
            "contact_number": phone_number,
            "name": customer.name,
            "stage": final_route or final_stage,
            "qualification_score": final_score,
            "budget_signal": final_state.get("budget_signal"),
            "timeline_signal": final_state.get("timeline_signal"),
            "need_summary": final_state.get("need_summary"),
            "route_destination": final_route
        }
    )

    firebase_service.record_conversation_message(
        business_id=business_id,
        customer_id=customer.id,
        role="assistant",
        content=reply_text,
        raw_payload={"stage": final_stage, "score": final_score}
    )

    # 9. Generate contextual Quick Reply chips
    quick_replies = []
    if final_stage == "greet":
        quick_replies = ["Running Shoes under ₹2,000", "Casual Sneakers", "Track Order #SH-8942", "7-Day Return Policy"]
    elif matched_products:
        p = matched_products[0]
        sizes = p.availableSizes or ["7", "8", "9", "10"]
        quick_replies = [f"Check size {s}" for s in sizes[:3]] + ["Delivery options", "Is Cash on Delivery available?"]
    else:
        quick_replies = ["Show Running Shoes", "Show Walking Shoes", "Under ₹2,000", "Talk to Human Rep"]

    return ChatMessageResponse(
        reply_text=reply_text,
        stage=final_route or final_stage,
        qualification_score=final_score,
        matched_products=verified_prods[:4],
        inventory_data=inventory_data,
        order_info=order_info,
        quick_replies=quick_replies,
        route_destination=final_route
    )
