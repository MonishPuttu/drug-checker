import json
from graph.state import AgentState
from tools.drug_api_tools import check_all_interactions, get_openfda_interactions
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


ANALYSIS_PROMPT = """You are a clinical pharmacist. Analyze these drug interaction findings and provide a structured assessment.

For each interaction found, rate it as:
- LOW: Minor interaction, usually not clinically significant
- MODERATE: May require dose adjustment or monitoring
- HIGH: Significant risk, requires medical intervention
- CONTRAINDICATED: Should not be used together

Return ONLY valid JSON:
{
  "interactions": [
    {
      "drug1": "drug_name",
      "drug2": "drug_name", 
      "severity": "MODERATE",
      "description": "Clinical description",
      "recommendation": "What to do",
      "source": "source_name"
    }
  ]
}"""


def interaction_node(state: AgentState) -> AgentState:
    drugs = state.get("drugs", [])
    if len(drugs) < 1:
        return {**state, "interactions": []}

    drug_names = [d["name"] for d in drugs if d.get("name")]

    api_interactions = check_all_interactions(drug_names)

    fda_warnings = []
    for name in drug_names:
        fda_warnings.extend(get_openfda_interactions(name))

    all_findings = {
        "api_interactions": api_interactions,
        "fda_warnings": fda_warnings[:5],
        "drugs_checked": drug_names
    }

    if not api_interactions and not fda_warnings:
        try:
            llm = ChatOllama(model="llama3.2", temperature=0)
            drug_list = ", ".join(drug_names)
            messages = [
                SystemMessage(content=ANALYSIS_PROMPT),
                HumanMessage(content=f"Check interactions between these drugs: {drug_list}\n\nNo API data available, use your training knowledge.")
            ]
            response = llm.invoke(messages)
            content = response.content.strip()
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return {**state, "interactions": parsed.get("interactions", [])}
        except Exception:
            pass
        return {**state, "interactions": []}

    try:
        llm = ChatOllama(model="llama3.2", temperature=0)
        messages = [
            SystemMessage(content=ANALYSIS_PROMPT),
            HumanMessage(content=f"Analyze these drug interaction findings:\n{json.dumps(all_findings, indent=2)}")
        ]
        response = llm.invoke(messages)
        content = response.content.strip()
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            interactions = parsed.get("interactions", [])
        else:
            interactions = api_interactions

    except Exception:
        interactions = api_interactions

    return {**state, "interactions": interactions}
