import json
import re
from graph.state import AgentState
from tools.pubmed_tool import search_drug_safety
from tools.drug_api_tools import search_openfda_adverse_events
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


SYNTHESIS_PROMPT = """You are a clinical researcher. Summarize the following medical literature findings about drug safety.

Focus on:
- Key safety concerns
- Important drug interactions mentioned
- Recent warnings or updates
- Clinical significance

Return ONLY valid JSON:
{
  "web_findings": [
    {
      "finding": "Summary of finding",
      "drugs_involved": ["drug1"],
      "clinical_significance": "HIGH/MODERATE/LOW",
      "source": "source name"
    }
  ]
}"""


def web_search_node(state: AgentState) -> AgentState:
    drugs = state.get("drugs", [])
    if not drugs:
        return {**state, "web_findings": []}

    drug_names = [d["name"] for d in drugs if d.get("name")]
    all_pubmed = []
    all_adverse = []

    for i, drug in enumerate(drug_names):
        for other in drug_names[i+1:]:
            results = search_drug_safety(drug, other)
            all_pubmed.extend(results)

    for drug in drug_names[:3]:  # limit to first 3 to avoid rate limits
        adverse = search_openfda_adverse_events(drug)
        all_adverse.extend(adverse[:3])

    if not all_pubmed and not all_adverse:
        return {**state, "web_findings": []}

    findings_context = {
        "pubmed_results": all_pubmed[:6],
        "adverse_events": all_adverse[:9],
        "drugs": drug_names
    }

    try:
        llm = ChatOllama(model="llama3.2", temperature=0)
        messages = [
            SystemMessage(content=SYNTHESIS_PROMPT),
            HumanMessage(content=f"Synthesize these findings:\n{json.dumps(findings_context, indent=2)}")
        ]
        response = llm.invoke(messages)
        content = response.content.strip()

        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            web_findings = parsed.get("web_findings", [])
        else:
            web_findings = []

    except Exception:
        web_findings = []

    return {**state, "web_findings": web_findings}
