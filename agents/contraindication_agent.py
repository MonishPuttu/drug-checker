import json
import re
from graph.state import AgentState
from tools.drug_api_tools import get_openfda_interactions
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


CONTRAINDICATION_PROMPT = """You are a clinical pharmacist AI specializing in contraindications.

Given a list of drugs and patient information, identify any contraindications based on:
1. Patient conditions (e.g., renal failure, liver disease, pregnancy)
2. Patient allergies
3. Patient age (pediatric/geriatric considerations)
4. Drug-disease interactions

Return ONLY valid JSON:
{
  "contraindications": [
    {
      "drug": "drug_name",
      "condition": "condition or allergy",
      "severity": "HIGH",
      "description": "Why this is contraindicated",
      "recommendation": "What to do instead",
      "source": "Clinical knowledge"
    }
  ]
}

If no contraindications are found, return: {"contraindications": []}"""


RULE_BASED_CONTRAINDICATIONS = {
    "warfarin": [
        {
            "condition": "pregnancy",
            "severity": "HIGH",
            "description": "Warfarin can cause fetal harm and major congenital malformations.",
            "recommendation": "Avoid during pregnancy unless absolutely necessary and specialist-supervised.",
            "source": "RuleBasedKnowledge",
        },
        {
            "condition": "active bleeding",
            "severity": "HIGH",
            "description": "Warfarin is contraindicated in active major bleeding.",
            "recommendation": "Use non-anticoagulant options until bleeding is controlled.",
            "source": "RuleBasedKnowledge",
        },
    ],
    "aspirin": [
        {
            "condition": "active peptic ulcer or bleeding disorder",
            "severity": "HIGH",
            "description": "Aspirin can worsen bleeding and may precipitate GI hemorrhage.",
            "recommendation": "Avoid aspirin and consider safer alternatives when bleeding risk is high.",
            "source": "RuleBasedKnowledge",
        },
        {
            "condition": "aspirin-exacerbated respiratory disease / NSAID hypersensitivity",
            "severity": "HIGH",
            "description": "Aspirin may trigger bronchospasm or severe hypersensitivity reactions.",
            "recommendation": "Avoid aspirin in known NSAID-sensitive asthma or prior hypersensitivity.",
            "source": "RuleBasedKnowledge",
        },
    ],
}


def _rule_based_contraindications(drug_names):
    items = []
    for drug in sorted({(d or "").lower().strip() for d in drug_names if d}):
        for entry in RULE_BASED_CONTRAINDICATIONS.get(drug, []):
            items.append({"drug": drug, **entry})
    return items


def _openfda_contraindications(drug_names):
    items = []
    for drug in drug_names:
        for finding in get_openfda_interactions(drug):
            if finding.get("type") != "contraindication":
                continue
            items.append({
                "drug": drug,
                "condition": "FDA label contraindication",
                "severity": "HIGH",
                "description": finding.get("text", ""),
                "recommendation": "Avoid use if contraindication applies; review full label and patient history.",
                "source": finding.get("source", "OpenFDA"),
            })
    return items


def _dedupe_contraindications(items):
    seen = set()
    deduped = []
    for item in items:
        drug = (item.get("drug") or "").lower().strip()
        condition = (item.get("condition") or "").lower().strip()
        if not drug or not condition:
            continue
        key = (drug, condition)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def contraindication_node(state: AgentState) -> AgentState:
    drugs = state.get("drugs", [])
    patient_info = state.get("patient_info", {})

    if not drugs:
        return {**state, "contraindications": []}

    drug_names = [d["name"] for d in drugs if d.get("name")]
    rule_based = _rule_based_contraindications(drug_names)
    fda_based = _openfda_contraindications(drug_names)

    patient_str = ""
    if patient_info:
        conditions = patient_info.get("conditions", [])
        allergies = patient_info.get("allergies", [])
        age = patient_info.get("age")
        if age:
            patient_str += f"Age: {age}\n"
        if conditions:
            patient_str += f"Conditions: {', '.join(conditions)}\n"
        if allergies:
            patient_str += f"Allergies: {', '.join(allergies)}\n"

    if not patient_str:
        patient_str = "No specific patient information provided. Check general contraindications."

    try:
        llm = ChatOllama(model="llama3.2", temperature=0)
        messages = [
            SystemMessage(content=CONTRAINDICATION_PROMPT),
            HumanMessage(content=(
                f"Drugs prescribed: {', '.join(drug_names)}\n\n"
                f"Patient info:\n{patient_str}\n\n"
                f"Identify all contraindications."
            ))
        ]
        response = llm.invoke(messages)
        content = response.content.strip()

        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            contraindications = parsed.get("contraindications", [])
        else:
            contraindications = []

    except Exception:
        contraindications = []

    merged = _dedupe_contraindications(contraindications + fda_based + rule_based)
    return {**state, "contraindications": merged}
