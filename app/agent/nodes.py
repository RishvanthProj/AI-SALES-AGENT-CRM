from typing import Dict, Any
from app.agent.state import SalesAgentState
from app.services.claude_service import claude_service


def greet_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Greet Node:
    Welcomes the lead and introduces the business service.
    Graph controls state -> sets current_stage to 'greet'.
    """
    reply = claude_service.generate_stage_copy(
        current_stage="greet",
        lead_name=state.get("lead_name"),
        conversation_history=state.get("history", []),
        extracted_signals={}
    )
    return {
        "current_stage": "greet",
        "reply_text": reply
    }


def qualify_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Qualify Node:
    Extracts the user's primary requirement/need using Claude structured extraction.
    Graph controls state -> sets current_stage to 'qualify'.
    """
    incoming = state.get("incoming_message", "")
    need_data = claude_service.extract_need(
        message_text=incoming,
        conversation_history=state.get("history", [])
    )

    reply = claude_service.generate_stage_copy(
        current_stage="qualify",
        lead_name=state.get("lead_name"),
        conversation_history=state.get("history", []),
        extracted_signals={"need": need_data.summary}
    )

    return {
        "current_stage": "qualify",
        "need_summary": need_data.summary,
        "reply_text": reply
    }


def collect_budget_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Collect Budget Node:
    Extracts structured budget signal from incoming message.
    Graph controls state -> sets current_stage to 'collect_budget'.
    """
    incoming = state.get("incoming_message", "")
    budget_data = claude_service.extract_budget(message_text=incoming)

    # Preserve existing budget_signal if already populated
    current_budget = state.get("budget_signal") or budget_data.budget_range

    reply = claude_service.generate_stage_copy(
        current_stage="collect_budget",
        lead_name=state.get("lead_name"),
        conversation_history=state.get("history", []),
        extracted_signals={"budget_signal": current_budget}
    )

    return {
        "current_stage": "collect_budget",
        "budget_signal": current_budget,
        "reply_text": reply
    }


def collect_timeline_node(state: SalesAgentState) -> Dict[str, Any]:
    """
    Collect Timeline Node:
    Extracts structured timeline signal from incoming message.
    Graph controls state -> sets current_stage to 'collect_timeline'.
    """
    incoming = state.get("incoming_message", "")
    timeline_data = claude_service.extract_timeline(message_text=incoming)

    current_timeline = state.get("timeline_signal") or timeline_data.timeline_str

    reply = claude_service.generate_stage_copy(
        current_stage="collect_timeline",
        lead_name=state.get("lead_name"),
        conversation_history=state.get("history", []),
        extracted_signals={
            "budget_signal": state.get("budget_signal"),
            "timeline_signal": current_timeline
        }
    )

    return {
        "current_stage": "collect_timeline",
        "timeline_signal": current_timeline,
        "reply_text": reply
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
    Determines next business routing stage based strictly on score and budget constraint:
    - Score >= 70 AND budget_signal is present -> 'quoted'
    - Score < 40 -> 'nurture'
    - Otherwise -> 'human_handoff'

    The LLM only generates the final closing message matching this decision.
    """
    score = state.get("qualification_score", 0.0)
    has_budget = bool(state.get("budget_signal") and str(state.get("budget_signal")).strip())

    if score >= 70.0 and has_budget:
        destination = "quoted"
    elif score < 40.0:
        destination = "nurture"
    else:
        destination = "human_handoff"

    reply = claude_service.generate_stage_copy(
        current_stage="route",
        lead_name=state.get("lead_name"),
        conversation_history=state.get("history", []),
        extracted_signals={
            "score": score,
            "route": destination,
            "budget_signal": state.get("budget_signal"),
            "timeline_signal": state.get("timeline_signal")
        }
    )

    return {
        "current_stage": "route",
        "route_destination": destination,
        "reply_text": reply
    }
