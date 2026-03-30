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


def contraindication_node(state: AgentState) -> AgentState:
    drugs = state.get("drugs", [])
    patient_info = state.get("patient_info", {})

    if not drugs:
        return {**state, "contraindications": []}

    drug_names = [d["name"] for d in drugs if d.get("name")]

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

    except Exception as e:
        contraindications = []

    return {**state, "contraindications": contraindications}
