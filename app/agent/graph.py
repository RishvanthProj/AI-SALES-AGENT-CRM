from langgraph.graph import StateGraph, END
from app.agent.state import SalesAgentState
from app.agent.nodes import (
    greet_node,
    qualify_node,
    collect_budget_node,
    collect_timeline_node,
    score_node,
    route_node
)


def build_sales_qualification_graph():
    """
    Constructs the deterministic LangGraph state machine skeleton:
    greet -> qualify -> collect_budget -> collect_timeline -> score -> route -> END

    The graph enforces all stage transitions; the LLM only performs structured field extraction
    and copywriting inside the nodes.
    """
    workflow = StateGraph(SalesAgentState)

    # Add Nodes
    workflow.add_node("greet", greet_node)
    workflow.add_node("qualify", qualify_node)
    workflow.add_node("collect_budget", collect_budget_node)
    workflow.add_node("collect_timeline", collect_timeline_node)
    workflow.add_node("score", score_node)
    workflow.add_node("route", route_node)

    # Set Entry Point
    workflow.set_entry_point("greet")

    # Add Deterministic Edges
    workflow.add_edge("greet", "qualify")
    workflow.add_edge("qualify", "collect_budget")
    workflow.add_edge("collect_budget", "collect_timeline")
    workflow.add_edge("collect_timeline", "score")
    workflow.add_edge("score", "route")
    workflow.add_edge("route", END)

    return workflow.compile()


# Compiled Singleton Graph
sales_graph = build_sales_qualification_graph()
