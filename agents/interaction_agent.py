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


RULE_BASED_INTERACTIONS = {
    frozenset(["warfarin", "aspirin"]): {
        "severity": "HIGH",
        "description": "Concomitant use increases bleeding risk because both agents affect hemostasis.",
        "recommendation": "Avoid combination when possible or monitor INR and bleeding closely.",
        "source": "RuleBasedKnowledge"
    },
    frozenset(["warfarin", "ibuprofen"]): {
        "severity": "HIGH",
        "description": "Combined anticoagulant and NSAID effect increases risk of major bleeding.",
        "recommendation": "Prefer non-NSAID analgesics and monitor for bleeding signs.",
        "source": "RuleBasedKnowledge"
    },
    frozenset(["sertraline", "tramadol"]): {
        "severity": "HIGH",
        "description": "Combination may increase serotonin syndrome and seizure risk.",
        "recommendation": "Use alternative analgesic or monitor closely for serotonin toxicity.",
        "source": "RuleBasedKnowledge"
    },
    frozenset(["fluoxetine", "tramadol"]): {
        "severity": "HIGH",
        "description": "Combination may increase serotonin syndrome and seizure risk.",
        "recommendation": "Use alternative analgesic or monitor closely for serotonin toxicity.",
        "source": "RuleBasedKnowledge"
    },
}


def _rule_based_interactions(drug_names):
    normalized = sorted({(d or "").lower().strip() for d in drug_names if d})
    findings = []
    for i, drug1 in enumerate(normalized):
        for drug2 in normalized[i + 1:]:
            key = frozenset([drug1, drug2])
            payload = RULE_BASED_INTERACTIONS.get(key)
            if not payload:
                continue
            findings.append({
                "drug1": drug1,
                "drug2": drug2,
                "severity": payload["severity"],
                "description": payload["description"],
                "recommendation": payload["recommendation"],
                "source": payload["source"],
            })
    return findings


def _dedupe_interactions(interactions):
    seen = set()
    deduped = []
    for item in interactions:
        d1 = (item.get("drug1") or "").lower().strip()
        d2 = (item.get("drug2") or "").lower().strip()
        key = tuple(sorted([d1, d2]))
        if not d1 or not d2 or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def interaction_node(state: AgentState) -> AgentState:
    drugs = state.get("drugs", [])
    if len(drugs) < 1:
        return {**state, "interactions": []}

    drug_names = [d["name"] for d in drugs if d.get("name")]

    api_interactions = check_all_interactions(drug_names)

    fda_warnings = []
    for name in drug_names:
        fda_warnings.extend(get_openfda_interactions(name))

    rule_based = _rule_based_interactions(drug_names)

    all_findings = {
        "api_interactions": api_interactions,
        "fda_warnings": fda_warnings[:5],
        "rule_based": rule_based,
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
                parsed_interactions = parsed.get("interactions", [])
                merged = _dedupe_interactions(parsed_interactions + rule_based)
                return {**state, "interactions": merged}
        except Exception:
            pass
        return {**state, "interactions": rule_based}

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

    merged = _dedupe_interactions(interactions + rule_based)
    return {**state, "interactions": merged}
