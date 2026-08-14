import uuid
import pytest
from app.agent.graph import sales_graph
from app.agent.state import SalesAgentState
from app.agent.nodes import greet_node, qualify_node, collect_budget_node, collect_timeline_node, score_node, route_node


def test_langgraph_deterministic_flow_execution():
    """
    Test Requirement:
    A LangGraph state machine skeleton with nodes greet → qualify → collect_budget → collect_timeline → score → route.
    The graph controls the state transitions; the LLM only generates language and extracts structured fields inside each node.
    """
    initial_state: SalesAgentState = {
        "tenant_id": str(uuid.uuid4()),
        "lead_id": str(uuid.uuid4()),
        "contact_number": "+14155551234",
        "lead_name": "Taylor Swift",
        "current_stage": "greet",
        "incoming_message": "We need custom solar panel installation with a budget of $25,000 within 2 weeks.",
        "need_summary": None,
        "budget_signal": None,
        "timeline_signal": None,
        "qualification_score": 0.0,
        "route_destination": None,
        "reply_text": "",
        "history": [],
        "error": None
    }

    # Execute graph
    final_state = sales_graph.invoke(initial_state)

    # 1. Verify stage reached the terminal route stage
    assert final_state["current_stage"] == "route"

    # 2. Verify all intermediate signal extractions were populated
    assert final_state["need_summary"] is not None
    assert final_state["budget_signal"] is not None
    assert "25,000" in str(final_state["budget_signal"])
    assert final_state["timeline_signal"] is not None

    # 3. Verify scoring was calculated deterministically
    # 30 (need) + 40 (budget) + 30 (timeline) = 100
    assert final_state["qualification_score"] == 100.0

    # 4. Verify routing decision: Score 100 >= 70 AND budget_signal present -> 'quoted'
    assert final_state["route_destination"] == "quoted"
    assert len(final_state["reply_text"]) > 0


def test_individual_node_isolation():
    """
    Verify each node executes its discrete responsibilities in isolation
    without the LLM altering the graph state progression.
    """
    state: SalesAgentState = {
        "tenant_id": str(uuid.uuid4()),
        "lead_id": str(uuid.uuid4()),
        "contact_number": "+14155554321",
        "lead_name": "Sam Altman",
        "current_stage": "start",
        "incoming_message": "Our budget is around 10k USD",
        "need_summary": "AI Infrastructure",
        "budget_signal": None,
        "timeline_signal": None,
        "qualification_score": 0.0,
        "route_destination": None,
        "reply_text": "",
        "history": [],
        "error": None
    }

    # Test collect_budget_node
    budget_out = collect_budget_node(state)
    assert budget_out["current_stage"] == "collect_budget"
    assert budget_out["budget_signal"] is not None
    assert "10k" in str(budget_out["budget_signal"]).lower() or "10" in str(budget_out["budget_signal"])

    # Test score_node with only budget populated
    state["budget_signal"] = "$10k"
    state["need_summary"] = "AI Infrastructure"
    state["timeline_signal"] = None
    score_out = score_node(state)
    assert score_out["qualification_score"] == 70.0 # 30 (need) + 40 (budget) = 70.0

    # Test route_node with score 70.0 and budget present -> 'quoted'
    state["qualification_score"] = 70.0
    route_out = route_node(state)
    assert route_out["route_destination"] == "quoted"

    # Test route_node when score is low (<40) -> 'nurture'
    state["qualification_score"] = 30.0
    state["budget_signal"] = None
    route_nurture_out = route_node(state)
    assert route_nurture_out["route_destination"] == "nurture"
