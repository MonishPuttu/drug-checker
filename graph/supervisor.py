from graph.state import AgentState


def supervisor_node(state: AgentState) -> AgentState:
    drugs = state.get("drugs", [])

    if not drugs:
        return {**state, "next": "ingestion", "error": None}

    has_interactions = bool(state.get("interactions"))
    has_contraindications = bool(state.get("contraindications"))
    has_web = bool(state.get("web_findings"))
    has_alternatives = bool(state.get("alternatives"))
    has_report = bool(state.get("report"))
    parallel_checks_complete = bool(state.get("parallel_checks_complete"))
    alternatives_complete = bool(state.get("alternatives_complete"))

    if has_report:
        return {**state, "next": "END"}

    if has_alternatives or alternatives_complete:
        return {**state, "next": "report"}

    if not parallel_checks_complete:
        if has_interactions and has_contraindications and has_web:
            return {**state, "next": "alternatives"}
        return {**state, "next": "parallel_check"}

    return {**state, "next": "alternatives"}
