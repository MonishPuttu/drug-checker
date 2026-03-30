from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel


class DrugInfo(BaseModel):
    name: str
    dose: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None


class Interaction(BaseModel):
    drug1: str
    drug2: str
    severity: str
    description: str
    source: str


class Contraindication(BaseModel):
    drug: str
    condition: str
    severity: str
    description: str


class Alternative(BaseModel):
    original_drug: str
    alternative_drug: str
    reason: str
    notes: str


class AgentState(TypedDict):
    raw_input: str
    input_type: str
    drugs: List[Dict[str, Any]]
    patient_info: Dict[str, Any]
    interactions: List[Dict[str, Any]]
    contraindications: List[Dict[str, Any]]
    web_findings: List[Dict[str, Any]]
    severity_score: str
    alternatives: List[Dict[str, Any]]
    report: Dict[str, Any]
    error: Optional[str]
    next: str
    parallel_checks_complete: bool
    alternatives_complete: bool
