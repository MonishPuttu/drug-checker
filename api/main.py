import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="RxCheck API")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

_graph = None
def get_graph():
    global _graph
    if _graph is None:
        from graph.builder import build_graph
        _graph = build_graph()
    return _graph

def base_state(raw_input, input_type, pi):
    return {"raw_input": raw_input, "input_type": input_type,
            "drugs": [], "patient_info": pi,
            "interactions": [], "contraindications": [],
            "web_findings": [], "severity_score": "SAFE",
            "alternatives": [], "report": {}, "error": None,
            "next": "ingestion", "parallel_checks_complete": False,
            "alternatives_complete": False}

class TextReq(BaseModel):
    prescription_text: str
    patient_age: Optional[int] = None
    patient_conditions: Optional[List[str]] = []
    patient_allergies: Optional[List[str]] = []

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/api/check/text")
async def check_text(req: TextReq):
    try:
        pi = {"age": req.patient_age,
              "conditions": req.patient_conditions or [],
              "allergies": req.patient_allergies or []}
        r = get_graph().invoke(base_state(req.prescription_text, "text", pi))
        return r.get("report") or {}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/check/pdf")
async def check_pdf(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as t:
            t.write(await file.read()); path = t.name
        r = get_graph().invoke(base_state(path, "pdf", {}))
        try: os.unlink(path)
        except: pass
        return r.get("report") or {}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.post("/api/check/image")
async def check_image(file: UploadFile = File(...)):
    try:
        filename = file.filename or ""
        ext = os.path.splitext(filename)[1] or ".png"
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as t:
            t.write(await file.read())
            path = t.name
        r = get_graph().invoke(base_state(path, "image", {}))
        try:
            os.unlink(path)
        except Exception:
            pass
        return r.get("report") or {}
    except Exception as e:
        raise HTTPException(500, str(e))

static_dir = os.path.join(os.path.dirname(__file__), "../static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)