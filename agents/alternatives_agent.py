import json
import re
from graph.state import AgentState
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


ALTERNATIVES_PROMPT = """You are a senior clinical pharmacist. Based on the drug interactions and contraindications found, suggest safer alternatives.

Guidelines:
- Only suggest alternatives for drugs involved in HIGH or MODERATE severity interactions
- Suggest drugs from the same therapeutic class when possible
- Consider the patient's conditions when suggesting alternatives
- Be specific about why the alternative is safer

Return ONLY valid JSON:
{
  "alternatives": [
    {
      "original_drug": "drug_name",
      "reason_for_change": "Why this drug needs replacement",
      "alternatives": [
        {
          "name": "alternative_drug",
          "class": "therapeutic_class",
          "rationale": "Why this is safer",
          "notes": "Monitoring or dosing notes"
        }
      ]
    }
  ]
}

If no alternatives are needed (all drugs are safe), return: {"alternatives": []}"""


def alternatives_node(state: AgentState) -> AgentState:
    drugs = state.get("drugs", [])
    interactions = state.get("interactions", [])
    contraindications = state.get("contraindications", [])
    patient_info = state.get("patient_info", {})
    severity_score = state.get("severity_score", "SAFE")

    if severity_score in ("SAFE", "LOW") and not contraindications:
        return {**state, "alternatives": [], "alternatives_complete": True}

    drug_names = [d["name"] for d in drugs if d.get("name")]

    concerning_interactions = [
        i for i in interactions
        if i.get("severity", "LOW").upper() in ("HIGH", "MODERATE", "CRITICAL", "CONTRAINDICATED")
    ]

    context = {
        "drugs": drug_names,
        "patient_info": patient_info,
        "concerning_interactions": concerning_interactions,
        "contraindications": contraindications,
        "overall_severity": severity_score
    }

    try:
        llm = ChatOllama(model="llama3.2", temperature=0.2)
        messages = [
            SystemMessage(content=ALTERNATIVES_PROMPT),
            HumanMessage(content=f"Suggest alternatives based on:\n{json.dumps(context, indent=2)}")
        ]
        response = llm.invoke(messages)
        content = response.content.strip()

        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            alternatives = parsed.get("alternatives", [])
        else:
            alternatives = []

    except Exception:
        alternatives = []

    return {**state, "alternatives": alternatives, "alternatives_complete": True}
