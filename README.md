# Drug Interaction Checker

<!-- brag:start -->
<p align="center">
  <a href="brag-output/brag.mp4"><img src="brag-output/brag.gif" alt="RxCheck launch video" width="100%"></a>
  <br>
  <sub>▶ <a href="brag-output/brag.mp4"><b>Watch the full launch video with voice-over</b></a> (42s, sound on)</sub>
</p>
<!-- brag:end -->


### AI-powered multi-agent prescription safety system

**Stack:** LangGraph · LangChain · Ollama (Llama 3.2) · OpenFDA · RxNorm · PubMed · FastAPI · Streamlit

## Installation

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

# 4. Pull the Ollama model
ollama pull llama3.2
```

## CLI Output

![Screenshot](assets/Screenshot-2026-03-30-103517.png)

## Sample Prescriptions to Test

| Scenario              | Prescription                                                          |
| --------------------- | --------------------------------------------------------------------- |
| High severity         | `Warfarin 5mg OD, Aspirin 81mg OD`                                    |
| Serotonin risk        | `Sertraline 50mg OD, Tramadol 50mg TID`                               |
| Renal concern         | `Metformin 1000mg BD, Contrast media`                                 |
| Safe combo            | `Amlodipine 5mg OD, Atorvastatin 40mg OD`                             |
| Complex poly-pharmacy | `Warfarin 5mg, Aspirin 81mg, Ibuprofen 400mg TID, Fluoxetine 20mg OD` |

---

## Architecture

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
