from typing import Dict, Any, List, Optional
from app.agent.state import SalesAgentState
from app.services.ai_service_factory import get_ai_provider
from app.services.firebase_service import firebase_service
from app.services.validation_service import validation_service
from app.schemas.ai import GroundedResponseContext


def greet_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Greet Node:
    Welcomes the lead naturally, introduces the business, handles small talk.
    Graph controls state -> sets current_stage to 'greet'.
    """
    ai = get_ai_provider()
    tenant_id = state.get("tenant_id", "default")
    incoming = state.get("incoming_message", "")
    history = state.get("history", [])

    if state.get("extracted_sales"):
        from app.schemas.ai import SalesExtraction
        sales_info = SalesExtraction(**state["extracted_sales"])
    else:
        sales_info = ai.extract_sales_signals(incoming, history)
    b_settings = firebase_service.get_business_settings(tenant_id)

    reply_text = state.get("reply_text")
    if not reply_text:
        context = GroundedResponseContext(
            business_name=b_settings.business_name,
            business_description=b_settings.business_description,
            current_stage="greet",
            lead_name=state.get("lead_name"),
            conversation_history=history,
            customer_message=incoming,
            known_signals={"intent": sales_info.intent}
        )

        reply = ai.generate_conversational_response(context)
        val_res = validation_service.validate_and_sanitize_response(
            generated_reply=reply,
            verified_products=[],
            inventory_data=None,
            business_settings=b_settings,
            customer_message=incoming
        )
        reply_text = val_res.sanitized_text

    return {
        "current_stage": "greet",
        "extracted_sales": sales_info.model_dump(),
        "is_inappropriate": sales_info.inappropriate_content,
        "is_jailbreak": sales_info.is_jailbreak_attempt,
        "reply_text": reply_text
    }


def qualify_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Qualify Node:
    Extracts the user's primary requirement/product query and looks up authentic
    products from Firebase.
    Graph controls state -> sets current_stage to 'qualify'.
    """
    ai = get_ai_provider()
    tenant_id = state.get("tenant_id", "default")
    incoming = state.get("incoming_message", "")
    history = state.get("history", [])

    if state.get("extracted_sales"):
        from app.schemas.ai import SalesExtraction
        sales_info = SalesExtraction(**state["extracted_sales"])
    else:
        sales_info = ai.extract_sales_signals(incoming, history)

    b_settings = firebase_service.get_business_settings(tenant_id)

    # Query Firebase for authentic matching products
    query_text = sales_info.product_query or incoming
    found_products = firebase_service.search_products(
        business_id=tenant_id,
        query=query_text,
        max_budget=sales_info.budget,
        color=sales_info.color,
        size=sales_info.size
    )

    verified_prods = [p.model_dump() for p in found_products]
    inventory_data = None
    if found_products:
        inventory_data = firebase_service.check_inventory(
            business_id=tenant_id,
            product_id=found_products[0].id,
            size=sales_info.size,
            color=sales_info.color
        )

    need_summary = query_text if query_text.strip() else state.get("need_summary")

    return {
        "current_stage": "qualify",
        "need_summary": need_summary,
        "verified_products": verified_prods,
        "inventory_data": inventory_data,
        "extracted_sales": sales_info.model_dump(),
        "is_inappropriate": sales_info.inappropriate_content,
        "is_jailbreak": sales_info.is_jailbreak_attempt
    }


def collect_budget_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Collect Budget Node:
    Extracts structured budget signal from incoming message or previous state.
    Graph controls state -> sets current_stage to 'collect_budget'.
    """
    ext_data = state.get("extracted_sales") or {}
    budget_val = ext_data.get("budget")
    b_range = ext_data.get("budget_range") or (f"Rs. {int(budget_val)}" if budget_val else None)
    current_budget = state.get("budget_signal") or b_range

    return {
        "current_stage": "collect_budget",
        "budget_signal": current_budget
    }


def collect_timeline_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Collect Timeline Node:
    Extracts structured timeline signal from incoming message.
    Graph controls state -> sets current_stage to 'collect_timeline'.
    """
    ext_data = state.get("extracted_sales") or {}
    timeline_val = ext_data.get("timeline")
    current_timeline = state.get("timeline_signal") or timeline_val

    return {
        "current_stage": "collect_timeline",
        "timeline_signal": current_timeline
    }


def score_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Score Node:
    Deterministically computes qualification score (0-100) based on extracted signals.
    Rule:
    - Need clarity: up to 30 pts
    - Budget signal populated: +40 pts
    - Timeline signal populated: +30 pts
    """
    score = 0.0

    if state.get("need_summary"):
        score += 30.0

    if state.get("budget_signal") and str(state.get("budget_signal")).strip():
        score += 40.0

    if state.get("timeline_signal") and str(state.get("timeline_signal")).strip():
        score += 30.0

    return {
        "current_stage": "score",
        "qualification_score": score
    }


def route_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Route Node:
    Determines next business routing stage based strictly on score and constraints:
    - Score >= 70 AND budget_signal is present -> 'quoted'
    - Score < 40 -> 'nurture'
    - Otherwise (or if flagged for human) -> 'human_handoff'
    """
    ai = get_ai_provider()
    tenant_id = state.get("tenant_id", "default")
    score = state.get("qualification_score", 0.0)
    has_budget = bool(state.get("budget_signal") and str(state.get("budget_signal")).strip())
    is_inappropriate = state.get("is_inappropriate", False)

    if is_inappropriate:
        destination = "human_handoff"
    elif score >= 70.0 and has_budget:
        destination = "quoted"
    elif score < 40.0:
        destination = "nurture"
    else:
        destination = "human_handoff"

    b_settings = firebase_service.get_business_settings(tenant_id)
    history = state.get("history", [])
    incoming = state.get("incoming_message", "")

    reply_text = state.get("reply_text")
    if not reply_text:
        context = GroundedResponseContext(
            business_name=b_settings.business_name,
            business_description=b_settings.business_description,
            current_stage="route",
            lead_name=state.get("lead_name"),
            conversation_history=history,
            verified_products=state.get("verified_products", []),
            inventory_data=state.get("inventory_data"),
            customer_message=incoming,
            known_signals={
                "score": score,
                "route": destination,
                "budget_signal": state.get("budget_signal"),
                "timeline_signal": state.get("timeline_signal")
            }
        )

        reply = ai.generate_conversational_response(context)
        val_res = validation_service.validate_and_sanitize_response(
            generated_reply=reply,
            verified_products=state.get("verified_products", []),
            inventory_data=state.get("inventory_data"),
            business_settings=b_settings,
            customer_message=incoming
        )
        reply_text = val_res.sanitized_text

    return {
        "current_stage": "route",
        "route_destination": destination,
        "reply_text": reply_text
    }
