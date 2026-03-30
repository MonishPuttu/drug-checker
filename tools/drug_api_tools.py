import requests
import time
from typing import List, Dict, Any, Optional


OPENFDA_BASE = "https://api.fda.gov/drug"
RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"
DAILYMED_BASE = "https://dailymed.nlm.nih.gov/dailymed/services/v2"


def get_rxcui(drug_name: str) -> Optional[str]:
    """Get RxNorm concept unique identifier for a drug."""
    try:
        url = f"{RXNORM_BASE}/rxcui.json"
        r = requests.get(url, params={"name": drug_name, "search": 1}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            ids = data.get("idGroup", {}).get("rxnormId", [])
            return ids[0] if ids else None
    except Exception:
        pass
    return None


def get_drug_interactions_rxnorm(drug_name: str, other_drugs: List[str]) -> List[Dict[str, Any]]:
    """Check drug interactions using RxNorm Interaction API."""
    interactions = []
    rxcui = get_rxcui(drug_name)
    if not rxcui:
        return interactions

    try:
        url = f"{RXNORM_BASE}/interaction/interaction.json"
        r = requests.get(url, params={"rxcui": rxcui, "sources": "ONCHigh"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            groups = data.get("interactionTypeGroup", [])
            for group in groups:
                for itype in group.get("interactionType", []):
                    for pair in itype.get("interactionPair", []):
                        description = pair.get("description", "")
                        severity = pair.get("severity", "N/A").upper()
                        concepts = pair.get("interactionConcept", [])
                        drug_names_in_pair = [
                            c.get("minConceptItem", {}).get("name", "").lower()
                            for c in concepts
                        ]
                        for other in other_drugs:
                            if any(other.lower() in n for n in drug_names_in_pair):
                                interactions.append({
                                    "drug1": drug_name,
                                    "drug2": other,
                                    "severity": map_severity(severity),
                                    "description": description,
                                    "source": "RxNorm/ONCHigh"
                                })
    except Exception:
        pass
    return interactions


def map_severity(raw: str) -> str:
    raw = raw.upper()
    if "HIGH" in raw or "CONTRAINDICATED" in raw:
        return "HIGH"
    elif "MODERATE" in raw or "MEDIUM" in raw:
        return "MODERATE"
    elif "LOW" in raw or "MINOR" in raw:
        return "LOW"
    return "LOW"


def get_openfda_interactions(drug_name: str) -> List[Dict[str, Any]]:
    """Get drug interaction warnings from OpenFDA drug label API."""
    results = []
    try:
        url = f"{OPENFDA_BASE}/label.json"
        params = {
            "search": f'openfda.generic_name:"{drug_name}"',
            "limit": 1
        }
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            labels = data.get("results", [])
            if labels:
                label = labels[0]
                interactions_text = label.get("drug_interactions", [""])[0]
                warnings_text = label.get("warnings", [""])[0]
                contraindications_text = label.get("contraindications", [""])[0]

                if interactions_text:
                    results.append({
                        "drug": drug_name,
                        "type": "interaction_warning",
                        "text": interactions_text[:500],
                        "source": "OpenFDA"
                    })
                if contraindications_text:
                    results.append({
                        "drug": drug_name,
                        "type": "contraindication",
                        "text": contraindications_text[:500],
                        "source": "OpenFDA"
                    })
    except Exception:
        pass
    return results


def search_openfda_adverse_events(drug_name: str) -> List[Dict[str, Any]]:
    """Get top adverse events for a drug from FDA FAERS."""
    results = []
    try:
        url = f"{OPENFDA_BASE}/event.json"
        params = {
            "search": f'patient.drug.medicinalproduct:"{drug_name}"',
            "count": "patient.reaction.reactionmeddrapt.exact",
            "limit": 5
        }
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for item in data.get("results", [])[:5]:
                results.append({
                    "drug": drug_name,
                    "adverse_event": item.get("term", "Unknown"),
                    "count": item.get("count", 0),
                    "source": "FDA FAERS"
                })
    except Exception:
        pass
    return results


def get_dailymed_info(drug_name: str) -> Optional[Dict[str, Any]]:
    """Get drug information from DailyMed."""
    try:
        url = f"{DAILYMED_BASE}/spls.json"
        r = requests.get(url, params={"drug_name": drug_name, "pagesize": 1}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            items = data.get("data", [])
            if items:
                return {
                    "drug": drug_name,
                    "title": items[0].get("title", ""),
                    "source": "DailyMed"
                }
    except Exception:
        pass
    return None


def check_all_interactions(drugs: List[str]) -> List[Dict[str, Any]]:
    """Check interactions between all drug pairs."""
    all_interactions = []
    seen_pairs = set()

    for i, drug in enumerate(drugs):
        other_drugs = [d for j, d in enumerate(drugs) if j != i]
        interactions = get_drug_interactions_rxnorm(drug, other_drugs)
        for interaction in interactions:
            pair_key = tuple(sorted([interaction["drug1"], interaction["drug2"]]))
            if pair_key not in seen_pairs:
                seen_pairs.add(pair_key)
                all_interactions.append(interaction)
        time.sleep(0.2)  # Avoid hitting upstream API rate limits.

    return all_interactions
