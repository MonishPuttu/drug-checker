import requests
from typing import List, Dict, Any
import xml.etree.ElementTree as ET


PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_pubmed(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """Search PubMed for drug-related literature."""
    results = []
    try:
        search_url = f"{PUBMED_BASE}/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }
        r = requests.get(search_url, params=search_params, timeout=10)
        if r.status_code != 200:
            return results

        ids = r.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return results

        fetch_url = f"{PUBMED_BASE}/efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "rettype": "abstract",
            "retmode": "xml"
        }
        r = requests.get(fetch_url, params=fetch_params, timeout=10)
        if r.status_code != 200:
            return results

        root = ET.fromstring(r.text)
        for article in root.findall(".//PubmedArticle"):
            title_el = article.find(".//ArticleTitle")
            abstract_el = article.find(".//AbstractText")
            pmid_el = article.find(".//PMID")

            title = title_el.text if title_el is not None else "No title"
            abstract = abstract_el.text if abstract_el is not None else "No abstract"
            pmid = pmid_el.text if pmid_el is not None else ""

            results.append({
                "title": title,
                "abstract": abstract[:300] if abstract else "",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source": "PubMed"
            })

    except Exception as e:
        results.append({"error": str(e), "source": "PubMed"})

    return results


def search_drug_safety(drug1: str, drug2: str = None) -> List[Dict[str, Any]]:
    """Search for drug safety information on PubMed."""
    if drug2:
        query = f"{drug1} {drug2} drug interaction safety"
    else:
        query = f"{drug1} adverse effects safety warnings"
    return search_pubmed(query, max_results=2)
