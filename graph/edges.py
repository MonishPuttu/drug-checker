from graph.state import AgentState


def route_after_supervisor(state: AgentState) -> str:
    return state.get("next", "END")


def route_after_ingestion(state: AgentState) -> str:
    if state.get("error"):
        return "END"
    drugs = state.get("drugs", [])
    if not drugs:
        return "END"
    return "supervisor"


def route_after_parallel(state: AgentState) -> str:
    return "aggregator"


def route_after_aggregator(state: AgentState) -> str:
    return "supervisor"


def route_after_alternatives(state: AgentState) -> str:
    return "supervisor"


def route_after_report(state: AgentState) -> str:
    return "END"
