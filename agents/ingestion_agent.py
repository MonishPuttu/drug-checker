import re
import json
from graph.state import AgentState
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage


SYSTEM_PROMPT = """You are a clinical pharmacist AI. Your job is to extract structured drug information from prescription text.

Extract ALL drugs mentioned along with:
- name (generic name preferred)
- dose (e.g., "500mg")
- frequency (e.g., "twice daily", "TID")
- route (e.g., "oral", "IV", "topical")

Also extract any patient information mentioned:
- age
- conditions/diagnoses
- allergies
- weight

Return ONLY valid JSON in this exact format:
{
  "drugs": [
    {"name": "metformin", "dose": "500mg", "frequency": "twice daily", "route": "oral"}
  ],
  "patient_info": {
    "age": null,
    "conditions": [],
    "allergies": [],
    "weight": null
  }
}

If a field is unknown, use null or empty list. Do NOT add any explanation outside the JSON."""

DRUG_REGEX = re.compile(
    r'\b(metformin|aspirin|warfarin|lisinopril|atorvastatin|omeprazole|amoxicillin|'
    r'ibuprofen|paracetamol|acetaminophen|clopidogrel|simvastatin|amlodipine|'
    r'metoprolol|losartan|hydrochlorothiazide|gabapentin|sertraline|fluoxetine|'
    r'ciprofloxacin|doxycycline|prednisone|levothyroxine|insulin|tramadol|'
    r'diazepam|alprazolam|atenolol|ramipril|pantoprazole|esomeprazole|'
    r'rosuvastatin|furosemise|spironolactone|bisoprolol|'
    r'carvedilol|digoxin|amiodarone|apixaban|rivaroxaban|dabigatran)\b',
    re.IGNORECASE
)


def extract_text_from_pdf(file_path: str) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        return " ".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception:
        return ""


def extract_text_from_image_ocr(file_path: str) -> str:
    """Try Tesseract OCR. Returns empty string on any failure."""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(file_path).convert("L")
        text = pytesseract.image_to_string(img, config="--psm 6")
        return text.strip()
    except Exception:
        return ""


def extract_text_from_image_vision(file_path: str) -> str:
    """Fallback: send image to a vision-capable Ollama model."""
    try:
        import base64, io
        from PIL import Image

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        img = Image.open(io.BytesIO(image_bytes))
        if max(img.width, img.height) > 1500:
            img.thumbnail((1500, 1500), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format=img.format or "PNG")
            image_bytes = buf.getvalue()

        b64 = base64.b64encode(image_bytes).decode("utf-8")

        for model in ["llama3.2-vision", "llava", "moondream"]:
            try:
                import ollama as _ollama
                resp = _ollama.chat(
                    model=model,
                    messages=[{
                        "role": "user",
                        "content": (
                            "This is a prescription or medication label image. "
                            "List every drug name, dose, and frequency you can read. "
                            "Be concise and accurate."
                        ),
                        "images": [b64],
                    }]
                )
                return resp["message"]["content"].strip()
            except Exception:
                continue
    except Exception:
        pass
    return ""


def ingestion_node(state: AgentState) -> AgentState:
    raw_input = state.get("raw_input", "")
    input_type = state.get("input_type", "text")

    if input_type == "pdf":
        text = extract_text_from_pdf(raw_input)
        if not text:
            return {**state, "drugs": [], "patient_info": {},
                    "error": "Could not extract text from PDF"}

    elif input_type == "image":
        text = extract_text_from_image_ocr(raw_input)
        if len(text) < 20:
            text = extract_text_from_image_vision(raw_input)
        if not text:
            return {**state, "drugs": [], "patient_info": {},
                    "error": (
                        "Could not read the image. Ensure Tesseract is installed, "
                        "or install a vision Ollama model (llama3.2-vision / llava)."
                    )}
    else:
        text = raw_input

    if not text.strip():
        return {**state, "drugs": [], "patient_info": {}, "error": "No text provided"}

    try:
        llm = ChatOllama(model="llama3.2", temperature=0)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Extract drug information from this prescription:\n\n{text}")
        ]
        response = llm.invoke(messages)
        content = response.content.strip()

        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        parsed = json.loads(json_match.group() if json_match else content)

        drugs = parsed.get("drugs", [])
        patient_info = parsed.get("patient_info", {})

        for drug in drugs:
            if drug.get("name"):
                drug["name"] = drug["name"].lower().strip()

        if drugs:
            return {**state, "drugs": drugs, "patient_info": patient_info, "error": None}
        raise ValueError("LLM returned no drugs")

    except Exception:
        pass

    found = set(m.lower() for m in DRUG_REGEX.findall(text))
    drugs = [{"name": d, "dose": None, "frequency": None, "route": "oral"} for d in found]

    return {
        **state,
        "drugs": drugs,
        "patient_info": {},
        "error": None if drugs else "No drugs could be identified from the input"
    }
