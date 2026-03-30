from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.supervisor import supervisor_node
from graph.edges import route_after_supervisor, route_after_ingestion
from agents.ingestion_agent import ingestion_node
from agents.interaction_agent import interaction_node
from agents.contraindication_agent import contraindication_node
from agents.web_search_agent import web_search_node
from agents.alternatives_agent import alternatives_node
from agents.report_agent import report_node


def parallel_check_node(state: AgentState) -> AgentState:
    state = interaction_node(state)
    state = contraindication_node(state)
    state = web_search_node(state)
    return {**state, "parallel_checks_complete": True}


def aggregator_node(state: AgentState) -> AgentState:
    interactions = state.get("interactions", [])
    contraindications = state.get("contraindications", [])
    severity_levels = {"SAFE": 0, "LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
    max_severity = "SAFE"

    for item in interactions:
        sev = item.get("severity", "LOW").upper()
        if sev == "CONTRAINDICATED":
            sev = "CRITICAL"
        if severity_levels.get(sev, 0) > severity_levels.get(max_severity, 0):
            max_severity = sev

    for item in contraindications:
        sev = item.get("severity", "LOW").upper()
        if severity_levels.get(sev, 0) > severity_levels.get(max_severity, 0):
            max_severity = sev

    return {**state, "severity_score": max_severity}


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("ingestion_agent", ingestion_node)
    workflow.add_node("supervisor_node", supervisor_node)
    workflow.add_node("parallel_check_node", parallel_check_node)
    workflow.add_node("aggregator_node", aggregator_node)
    workflow.add_node("alternatives_agent", alternatives_node)
    workflow.add_node("report_agent", report_node)

    workflow.set_entry_point("ingestion_agent")

    workflow.add_conditional_edges(
        "ingestion_agent",
        route_after_ingestion,
        {"supervisor": "supervisor_node", "END": END}
    )

    workflow.add_conditional_edges(
        "supervisor_node",
        route_after_supervisor,
        {
            "ingestion": "ingestion_agent",
            "parallel_check": "parallel_check_node",
            "alternatives": "alternatives_agent",
            "report": "report_agent",
            "END": END,
        }
    )

    workflow.add_edge("parallel_check_node", "aggregator_node")
    workflow.add_edge("aggregator_node", "supervisor_node")
    workflow.add_edge("alternatives_agent", "supervisor_node")
    workflow.add_edge("report_agent", END)

    return workflow.compile()
