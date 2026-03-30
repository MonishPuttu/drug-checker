# Drug Interaction Checker

### AI-powered multi-agent prescription safety system

**Stack:** LangGraph · LangChain · Ollama (Llama 3.2) · OpenFDA · RxNorm · PubMed · FastAPI · Streamlit

---

## 1. Prerequisites

| Tool      | Version | Install            |
| --------- | ------- | ------------------ |
| Python    | 3.10+   | https://python.org |
| Ollama    | latest  | https://ollama.com |
| Tesseract | 5.x     | See below          |

### Install Tesseract (for image/prescription OCR)

```bash
# macOS
brew install tesseract

# Ubuntu / Debian
sudo apt-get install tesseract-ocr

# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
```

---

## 2. Installation

```bash
# 1. Clone / unzip the project
cd drug_checker

# 2. Create virtual environment
python -m venv venv

# Activate:
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Pull the Ollama model (one-time, ~2GB download)
ollama pull llama3.2
```

---

## 3. Running the Application

### Option A — Streamlit UI (recommended)

```bash
# Make sure Ollama is running first:
ollama serve

# In a new terminal:
streamlit run ui/app.py
# Opens at: http://localhost:8501
```

### Option B — FastAPI REST backend

```bash
# Make sure Ollama is running first:
ollama serve

# In a new terminal:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
# API docs at: http://localhost:8000/docs
```

### Option C — Command Line

```bash
# Make sure Ollama is running first:
ollama serve

# Simple text check:
python run.py "Warfarin 5mg once daily, Aspirin 81mg once daily"

# With patient info:
python run.py "Metformin 1000mg BD, Lisinopril 10mg OD" \
  --age 70 \
  --conditions "Type 2 diabetes" "Hypertension" "Renal impairment" \
  --allergies "Penicillin"

# From PDF:
python run.py --file /path/to/prescription.pdf

# Raw JSON output:
python run.py "Warfarin 5mg, Aspirin 81mg" --json
```

---

## 4. Running Tests

```bash
# Run full test suite (no Ollama required — uses mocks):
python tests/test_suite.py

# Or with pytest:
pip install pytest
pytest tests/test_suite.py -v
```

---

## 5. API Usage Examples

### Check prescription text

```bash
curl -X POST http://localhost:8000/check/text \
  -H "Content-Type: application/json" \
  -d '{
    "prescription_text": "Warfarin 5mg once daily, Aspirin 81mg once daily, Omeprazole 20mg OD",
    "patient_age": 65,
    "patient_conditions": ["Atrial fibrillation"],
    "patient_allergies": []
  }'
```

### Upload PDF prescription

```bash
curl -X POST http://localhost:8000/check/pdf \
  -F "file=@/path/to/prescription.pdf"
```

### Upload image prescription

```bash
curl -X POST http://localhost:8000/check/image \
  -F "file=@/path/to/prescription.jpg"
```

---

## 6. Project Structure

```
drug_checker/
├── graph/
│   ├── state.py          # TypedDict state schema
│   ├── supervisor.py     # Routing logic
│   ├── edges.py          # Edge conditions
│   └── builder.py        # LangGraph assembly
├── agents/
│   ├── ingestion_agent.py        # OCR + drug extraction
│   ├── interaction_agent.py      # DDI checking
│   ├── contraindication_agent.py # Patient safety checks
│   ├── web_search_agent.py       # PubMed + FDA lookup
│   ├── alternatives_agent.py     # Safer substitutes
│   └── report_agent.py           # Final report generation
├── tools/
│   ├── drug_api_tools.py  # OpenFDA + RxNorm APIs
│   └── pubmed_tool.py     # PubMed NCBI API
├── api/
│   └── main.py           # FastAPI backend
├── ui/
│   └── app.py            # Streamlit frontend
├── tests/
│   └── test_suite.py     # Full test suite
├── run.py                # CLI runner
├── requirements.txt
└── README.md
```

---

## 7. Sample Prescriptions to Test

| Scenario              | Prescription                                                          |
| --------------------- | --------------------------------------------------------------------- |
| High severity         | `Warfarin 5mg OD, Aspirin 81mg OD`                                    |
| Serotonin risk        | `Sertraline 50mg OD, Tramadol 50mg TID`                               |
| Renal concern         | `Metformin 1000mg BD, Contrast media`                                 |
| Safe combo            | `Amlodipine 5mg OD, Atorvastatin 40mg OD`                             |
| Complex poly-pharmacy | `Warfarin 5mg, Aspirin 81mg, Ibuprofen 400mg TID, Fluoxetine 20mg OD` |

---

## 8. Architecture

```
Prescription Input
       │
  [Ingestion Agent]  ← OCR / PDF / Text parser
       │
  [LangGraph Supervisor]
       │
  ┌────┴────────────────┐
  │                     │                     │
[Interaction Agent] [Contraindication]  [Web Search Agent]
(RxNorm + OpenFDA)   Agent (LLM)        (PubMed + FAERS)
  │                     │                     │
  └────────────────┬────┘─────────────────────┘
                   │
            [Aggregator Node]
                   │
           [Alternatives Agent]
                   │
            [Report Generator]
                   │
            Clinical Report
```

---

## 9. Disclaimer

This system is for **informational purposes only** and does **not** constitute medical advice.
Always consult a qualified healthcare professional before making any medication changes.
