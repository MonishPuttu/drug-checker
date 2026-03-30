import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import tempfile
import json

from graph.builder import build_graph

app = FastAPI(
    title="Drug Interaction Checker API",
    description="AI-powered drug interaction checker using LangGraph + Ollama",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


class TextRequest(BaseModel):
    prescription_text: str
    patient_age: Optional[int] = None
    patient_conditions: Optional[list] = []
    patient_allergies: Optional[list] = []


@app.get("/")
def root():
    return {"message": "Drug Interaction Checker API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/check/text")
def check_text(request: TextRequest):
    """Check drug interactions from prescription text."""
    try:
        initial_state = {
            "raw_input": request.prescription_text,
            "input_type": "text",
            "drugs": [],
            "patient_info": {
                "age": request.patient_age,
                "conditions": request.patient_conditions or [],
                "allergies": request.patient_allergies or [],
            },
            "interactions": [],
            "contraindications": [],
            "web_findings": [],
            "severity_score": "SAFE",
            "alternatives": [],
            "report": {},
            "error": None,
            "next": "ingestion"
        }
        result = graph.invoke(initial_state)
        return result.get("report", {"error": "No report generated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check/pdf")
async def check_pdf(file: UploadFile = File(...)):
    """Check drug interactions from a prescription PDF."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        initial_state = {
            "raw_input": tmp_path,
            "input_type": "pdf",
            "drugs": [], "patient_info": {},
            "interactions": [], "contraindications": [],
            "web_findings": [], "severity_score": "SAFE",
            "alternatives": [], "report": {},
            "error": None, "next": "ingestion"
        }
        result = graph.invoke(initial_state)
        os.unlink(tmp_path)
        return result.get("report", {"error": "No report generated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check/image")
async def check_image(file: UploadFile = File(...)):
    """Check drug interactions from a prescription image."""
    allowed = [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Allowed formats: {allowed}")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        initial_state = {
            "raw_input": tmp_path,
            "input_type": "image",
            "drugs": [], "patient_info": {},
            "interactions": [], "contraindications": [],
            "web_findings": [], "severity_score": "SAFE",
            "alternatives": [], "report": {},
            "error": None, "next": "ingestion"
        }
        result = graph.invoke(initial_state)
        os.unlink(tmp_path)
        return result.get("report", {"error": "No report generated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
