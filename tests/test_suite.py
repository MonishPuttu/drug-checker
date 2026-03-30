#!/usr/bin/env python3
"""
Test suite for Drug Interaction Checker.
Runs unit and integration tests without requiring Ollama to be running.
Use: python tests/test_suite.py
"""
import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDrugAPITools(unittest.TestCase):

    def test_map_severity_high(self):
        from tools.drug_api_tools import map_severity
        self.assertEqual(map_severity("HIGH"), "HIGH")
        self.assertEqual(map_severity("CONTRAINDICATED"), "HIGH")

    def test_map_severity_moderate(self):
        from tools.drug_api_tools import map_severity
        self.assertEqual(map_severity("MODERATE"), "MODERATE")
        self.assertEqual(map_severity("MEDIUM"), "MODERATE")

    def test_map_severity_low(self):
        from tools.drug_api_tools import map_severity
        self.assertEqual(map_severity("LOW"), "LOW")
        self.assertEqual(map_severity("MINOR"), "LOW")
        self.assertEqual(map_severity("UNKNOWN"), "LOW")

    @patch("tools.drug_api_tools.requests.get")
    def test_get_rxcui_success(self, mock_get):
        from tools.drug_api_tools import get_rxcui
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "idGroup": {"rxnormId": ["41493"]}
        }
        result = get_rxcui("warfarin")
        self.assertEqual(result, "41493")

    @patch("tools.drug_api_tools.requests.get")
    def test_get_rxcui_not_found(self, mock_get):
        from tools.drug_api_tools import get_rxcui
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"idGroup": {}}
        result = get_rxcui("nonexistentdrug123")
        self.assertIsNone(result)

    @patch("tools.drug_api_tools.requests.get")
    def test_get_openfda_interactions(self, mock_get):
        from tools.drug_api_tools import get_openfda_interactions
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [{
                "drug_interactions": ["May increase bleeding risk with NSAIDs"],
                "warnings": ["Bleeding warning"],
                "contraindications": ["Active bleeding"]
            }]
        }
        results = get_openfda_interactions("warfarin")
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)

    @patch("tools.drug_api_tools.requests.get")
    def test_get_openfda_empty(self, mock_get):
        from tools.drug_api_tools import get_openfda_interactions
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"results": []}
        results = get_openfda_interactions("unknowndrug")
        self.assertEqual(results, [])


class TestPubMedTool(unittest.TestCase):

    @patch("tools.pubmed_tool.requests.get")
    def test_search_pubmed_success(self, mock_get):
        from tools.pubmed_tool import search_pubmed

        search_response = MagicMock()
        search_response.status_code = 200
        search_response.json.return_value = {
            "esearchresult": {"idlist": ["12345"]}
        }

        fetch_response = MagicMock()
        fetch_response.status_code = 200
        fetch_response.text = """<?xml version="1.0"?>
        <PubmedArticleSet>
          <PubmedArticle>
            <MedlineCitation><PMID>12345</PMID>
              <Article>
                <ArticleTitle>Warfarin aspirin interaction study</ArticleTitle>
                <Abstract><AbstractText>This study examines the interaction.</AbstractText></Abstract>
              </Article>
            </MedlineCitation>
          </PubmedArticle>
        </PubmedArticleSet>"""

        mock_get.side_effect = [search_response, fetch_response]
        results = search_pubmed("warfarin aspirin interaction", max_results=1)
        self.assertIsInstance(results, list)

    @patch("tools.pubmed_tool.requests.get")
    def test_search_pubmed_no_results(self, mock_get):
        from tools.pubmed_tool import search_pubmed
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"esearchresult": {"idlist": []}}
        results = search_pubmed("zzznoresults", max_results=1)
        self.assertEqual(results, [])


class TestGraphState(unittest.TestCase):

    def test_state_schema(self):
        from graph.state import AgentState
        state: AgentState = {
            "raw_input": "Warfarin 5mg",
            "input_type": "text",
            "drugs": [],
            "patient_info": {},
            "interactions": [],
            "contraindications": [],
            "web_findings": [],
            "severity_score": "SAFE",
            "alternatives": [],
            "report": {},
            "error": None,
            "next": "ingestion"
        }
        self.assertEqual(state["input_type"], "text")
        self.assertEqual(state["severity_score"], "SAFE")


class TestSupervisor(unittest.TestCase):

    def test_routes_to_ingestion_when_no_drugs(self):
        from graph.supervisor import supervisor_node
        state = {
            "drugs": [], "interactions": [], "contraindications": [],
            "web_findings": [], "alternatives": [], "report": {},
            "severity_score": "SAFE", "next": "", "error": None,
            "raw_input": "", "input_type": "text", "patient_info": {}
        }
        result = supervisor_node(state)
        self.assertEqual(result["next"], "ingestion")

    def test_routes_to_parallel_after_ingestion(self):
        from graph.supervisor import supervisor_node
        state = {
            "drugs": [{"name": "warfarin"}],
            "interactions": [], "contraindications": [],
            "web_findings": [], "alternatives": [], "report": {},
            "severity_score": "SAFE", "next": "", "error": None,
            "raw_input": "warfarin", "input_type": "text", "patient_info": {}
        }
        result = supervisor_node(state)
        self.assertEqual(result["next"], "parallel_check")

    def test_routes_to_alternatives_after_parallel(self):
        from graph.supervisor import supervisor_node
        state = {
            "drugs": [{"name": "warfarin"}],
            "interactions": [{"drug1": "warfarin", "drug2": "aspirin", "severity": "HIGH"}],
            "contraindications": [{"drug": "warfarin", "condition": "GI bleed", "severity": "HIGH"}],
            "web_findings": [{"finding": "test"}],
            "alternatives": [], "report": {},
            "severity_score": "HIGH", "next": "", "error": None,
            "raw_input": "warfarin", "input_type": "text", "patient_info": {}
        }
        result = supervisor_node(state)
        self.assertEqual(result["next"], "alternatives")

    def test_routes_to_report_after_alternatives(self):
        from graph.supervisor import supervisor_node
        state = {
            "drugs": [{"name": "warfarin"}],
            "interactions": [{"drug1": "warfarin", "drug2": "aspirin", "severity": "HIGH"}],
            "contraindications": [],
            "web_findings": [{"finding": "test"}],
            "alternatives": [{"original_drug": "warfarin", "alternatives": []}],
            "report": {},
            "severity_score": "HIGH", "next": "", "error": None,
            "raw_input": "warfarin", "input_type": "text", "patient_info": {}
        }
        result = supervisor_node(state)
        self.assertEqual(result["next"], "report")

    def test_routes_to_end_after_report(self):
        from graph.supervisor import supervisor_node
        state = {
            "drugs": [{"name": "warfarin"}],
            "interactions": [{"drug1": "a", "drug2": "b", "severity": "HIGH"}],
            "contraindications": [],
            "web_findings": [{"finding": "x"}],
            "alternatives": [{"original_drug": "warfarin", "alternatives": []}],
            "report": {"report_id": "DIC-001"},
            "severity_score": "HIGH", "next": "", "error": None,
            "raw_input": "warfarin", "input_type": "text", "patient_info": {}
        }
        result = supervisor_node(state)
        self.assertEqual(result["next"], "END")


class TestAggregator(unittest.TestCase):

    def test_aggregator_computes_high_severity(self):
        from graph.builder import aggregator_node
        state = {
            "interactions": [
                {"drug1": "warfarin", "drug2": "aspirin", "severity": "HIGH"}
            ],
            "contraindications": [],
            "web_findings": [],
            "drugs": [{"name": "warfarin"}],
            "severity_score": "SAFE",
            "raw_input": "", "input_type": "text", "patient_info": {},
            "alternatives": [], "report": {}, "error": None, "next": ""
        }
        result = aggregator_node(state)
        self.assertEqual(result["severity_score"], "HIGH")

    def test_aggregator_stays_safe_when_no_issues(self):
        from graph.builder import aggregator_node
        state = {
            "interactions": [],
            "contraindications": [],
            "web_findings": [],
            "drugs": [{"name": "metformin"}],
            "severity_score": "SAFE",
            "raw_input": "", "input_type": "text", "patient_info": {},
            "alternatives": [], "report": {}, "error": None, "next": ""
        }
        result = aggregator_node(state)
        self.assertEqual(result["severity_score"], "SAFE")

    def test_aggregator_escalates_from_contraindication(self):
        from graph.builder import aggregator_node
        state = {
            "interactions": [{"severity": "LOW"}],
            "contraindications": [{"severity": "HIGH"}],
            "web_findings": [],
            "drugs": [{"name": "warfarin"}],
            "severity_score": "SAFE",
            "raw_input": "", "input_type": "text", "patient_info": {},
            "alternatives": [], "report": {}, "error": None, "next": ""
        }
        result = aggregator_node(state)
        self.assertEqual(result["severity_score"], "HIGH")


class TestIngestionAgent(unittest.TestCase):

    @patch("agents.ingestion_agent.ChatOllama")
    def test_ingestion_extracts_drugs(self, mock_ollama_cls):
        from agents.ingestion_agent import ingestion_node
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = json.dumps({
            "drugs": [
                {"name": "warfarin", "dose": "5mg", "frequency": "once daily", "route": "oral"},
                {"name": "aspirin", "dose": "81mg", "frequency": "once daily", "route": "oral"}
            ],
            "patient_info": {"age": 65, "conditions": ["atrial fibrillation"], "allergies": []}
        })
        mock_ollama_cls.return_value = mock_llm

        state = {
            "raw_input": "Warfarin 5mg once daily, Aspirin 81mg once daily",
            "input_type": "text",
            "drugs": [], "patient_info": {},
            "interactions": [], "contraindications": [],
            "web_findings": [], "severity_score": "SAFE",
            "alternatives": [], "report": {},
            "error": None, "next": "ingestion"
        }
        result = ingestion_node(state)
        self.assertEqual(len(result["drugs"]), 2)
        drug_names = [d["name"] for d in result["drugs"]]
        self.assertIn("warfarin", drug_names)
        self.assertIn("aspirin", drug_names)
        self.assertIsNone(result["error"])

    @patch("agents.ingestion_agent.ChatOllama")
    def test_ingestion_handles_malformed_json(self, mock_ollama_cls):
        from agents.ingestion_agent import ingestion_node
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "Here are the drugs: warfarin and aspirin"
        mock_ollama_cls.return_value = mock_llm

        state = {
            "raw_input": "warfarin 5mg OD aspirin 81mg OD",
            "input_type": "text",
            "drugs": [], "patient_info": {},
            "interactions": [], "contraindications": [],
            "web_findings": [], "severity_score": "SAFE",
            "alternatives": [], "report": {},
            "error": None, "next": ""
        }
        result = ingestion_node(state)
        self.assertIsInstance(result["drugs"], list)

    def test_ingestion_empty_input(self):
        state = {
            "raw_input": "",
            "input_type": "text",
            "drugs": [], "patient_info": {},
            "interactions": [], "contraindications": [],
            "web_findings": [], "severity_score": "SAFE",
            "alternatives": [], "report": {},
            "error": None, "next": ""
        }
        with patch("agents.ingestion_agent.ChatOllama"):
            from agents.ingestion_agent import ingestion_node
            result = ingestion_node(state)
            self.assertIsNotNone(result.get("error"))


class TestContraindicationAgent(unittest.TestCase):

    @patch("agents.contraindication_agent.ChatOllama")
    def test_finds_contraindication(self, mock_ollama_cls):
        from agents.contraindication_agent import contraindication_node
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = json.dumps({
            "contraindications": [{
                "drug": "metformin",
                "condition": "renal failure",
                "severity": "HIGH",
                "description": "Metformin is contraindicated in renal failure due to lactic acidosis risk",
                "recommendation": "Use insulin instead",
                "source": "Clinical knowledge"
            }]
        })
        mock_ollama_cls.return_value = mock_llm

        state = {
            "drugs": [{"name": "metformin", "dose": "1000mg"}],
            "patient_info": {"age": 70, "conditions": ["renal failure"], "allergies": []},
            "interactions": [], "contraindications": [],
            "web_findings": [], "severity_score": "SAFE",
            "alternatives": [], "report": {},
            "raw_input": "", "input_type": "text",
            "error": None, "next": ""
        }
        result = contraindication_node(state)
        self.assertTrue(len(result["contraindications"]) > 0)
        self.assertEqual(result["contraindications"][0]["drug"], "metformin")

    @patch("agents.contraindication_agent.ChatOllama")
    def test_no_contraindications_when_safe(self, mock_ollama_cls):
        from agents.contraindication_agent import contraindication_node
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = json.dumps({"contraindications": []})
        mock_ollama_cls.return_value = mock_llm

        state = {
            "drugs": [{"name": "paracetamol", "dose": "500mg"}],
            "patient_info": {"age": 30, "conditions": [], "allergies": []},
            "interactions": [], "contraindications": [],
            "web_findings": [], "severity_score": "SAFE",
            "alternatives": [], "report": {},
            "raw_input": "", "input_type": "text",
            "error": None, "next": ""
        }
        result = contraindication_node(state)
        self.assertEqual(result["contraindications"], [])


class TestAlternativesAgent(unittest.TestCase):

    @patch("agents.alternatives_agent.ChatOllama")
    def test_suggests_alternatives_for_high_severity(self, mock_ollama_cls):
        from agents.alternatives_agent import alternatives_node
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = json.dumps({
            "alternatives": [{
                "original_drug": "warfarin",
                "reason_for_change": "High bleeding risk with aspirin",
                "alternatives": [{
                    "name": "apixaban",
                    "class": "Direct oral anticoagulant",
                    "rationale": "Lower bleeding risk, no need for monitoring",
                    "notes": "Adjust dose for renal function"
                }]
            }]
        })
        mock_ollama_cls.return_value = mock_llm

        state = {
            "drugs": [{"name": "warfarin"}, {"name": "aspirin"}],
            "interactions": [{"drug1": "warfarin", "drug2": "aspirin", "severity": "HIGH"}],
            "contraindications": [],
            "web_findings": [],
            "severity_score": "HIGH",
            "patient_info": {},
            "alternatives": [], "report": {},
            "raw_input": "", "input_type": "text",
            "error": None, "next": ""
        }
        result = alternatives_node(state)
        self.assertTrue(len(result["alternatives"]) > 0)

    def test_skips_alternatives_when_safe(self):
        state = {
            "drugs": [{"name": "metformin"}],
            "interactions": [],
            "contraindications": [],
            "web_findings": [],
            "severity_score": "SAFE",
            "patient_info": {},
            "alternatives": [], "report": {},
            "raw_input": "", "input_type": "text",
            "error": None, "next": ""
        }
        from agents.alternatives_agent import alternatives_node
        result = alternatives_node(state)
        self.assertEqual(result["alternatives"], [])


class TestReportAgent(unittest.TestCase):

    @patch("agents.report_agent.ChatOllama")
    def test_generates_report_structure(self, mock_ollama_cls):
        from agents.report_agent import report_node
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = json.dumps({
            "clinical_summary": "Patient is prescribed warfarin and aspirin which have a HIGH severity interaction.",
            "key_recommendations": [
                "Consider GI protection with PPI",
                "Monitor INR more frequently"
            ],
            "follow_up_required": True,
            "urgency": "URGENT"
        })
        mock_ollama_cls.return_value = mock_llm

        state = {
            "drugs": [{"name": "warfarin"}, {"name": "aspirin"}],
            "interactions": [{"drug1": "warfarin", "drug2": "aspirin", "severity": "HIGH",
                               "description": "Increased bleeding risk", "recommendation": "Monitor INR"}],
            "contraindications": [],
            "web_findings": [],
            "severity_score": "HIGH",
            "alternatives": [],
            "patient_info": {"age": 65},
            "report": {},
            "raw_input": "", "input_type": "text",
            "error": None, "next": ""
        }
        result = report_node(state)
        report = result["report"]

        self.assertIn("report_id", report)
        self.assertIn("generated_at", report)
        self.assertIn("overall_severity", report)
        self.assertIn("clinical_summary", report)
        self.assertIn("key_recommendations", report)
        self.assertIn("disclaimer", report)
        self.assertEqual(report["overall_severity"], "HIGH")
        self.assertEqual(report["urgency"], "URGENT")
        self.assertEqual(len(report["drugs_analyzed"]), 2)


class TestFullGraphMocked(unittest.TestCase):

    @patch("agents.report_agent.ChatOllama")
    @patch("agents.alternatives_agent.ChatOllama")
    @patch("agents.web_search_agent.ChatOllama")
    @patch("agents.contraindication_agent.ChatOllama")
    @patch("agents.interaction_agent.ChatOllama")
    @patch("agents.ingestion_agent.ChatOllama")
    @patch("tools.drug_api_tools.requests.get")
    @patch("tools.pubmed_tool.requests.get")
    def test_full_pipeline(
        self,
        mock_pubmed_get, mock_drug_get,
        mock_ingest_llm, mock_interact_llm,
        mock_contra_llm, mock_web_llm,
        mock_alt_llm, mock_report_llm
    ):
        from graph.builder import build_graph

        mock_drug_get.return_value.status_code = 200
        mock_drug_get.return_value.json.return_value = {"idGroup": {}, "results": []}
        mock_pubmed_get.return_value.status_code = 200
        mock_pubmed_get.return_value.json.return_value = {"esearchresult": {"idlist": []}}

        mock_ingest_llm.return_value.invoke.return_value.content = json.dumps({
            "drugs": [
                {"name": "warfarin", "dose": "5mg", "frequency": "once daily", "route": "oral"},
                {"name": "aspirin", "dose": "81mg", "frequency": "once daily", "route": "oral"}
            ],
            "patient_info": {"age": 65, "conditions": [], "allergies": []}
        })

        mock_interact_llm.return_value.invoke.return_value.content = json.dumps({
            "interactions": [{
                "drug1": "warfarin", "drug2": "aspirin",
                "severity": "HIGH",
                "description": "Significantly increases bleeding risk",
                "recommendation": "Use with caution, monitor INR",
                "source": "LLM"
            }]
        })

        mock_contra_llm.return_value.invoke.return_value.content = json.dumps({"contraindications": []})

        mock_web_llm.return_value.invoke.return_value.content = json.dumps({
            "web_findings": [{
                "finding": "Warfarin-aspirin combination increases GI bleeding risk",
                "drugs_involved": ["warfarin", "aspirin"],
                "clinical_significance": "HIGH",
                "source": "PubMed"
            }]
        })

        mock_alt_llm.return_value.invoke.return_value.content = json.dumps({
            "alternatives": [{
                "original_drug": "aspirin",
                "reason_for_change": "HIGH interaction with warfarin",
                "alternatives": [{
                    "name": "clopidogrel",
                    "class": "Antiplatelet",
                    "rationale": "Lower bleeding risk than aspirin with warfarin",
                    "notes": "Still monitor INR"
                }]
            }]
        })

        mock_report_llm.return_value.invoke.return_value.content = json.dumps({
            "clinical_summary": "HIGH severity interaction between warfarin and aspirin. Close monitoring required.",
            "key_recommendations": ["Monitor INR weekly", "Consider GI prophylaxis"],
            "follow_up_required": True,
            "urgency": "URGENT"
        })

        graph = build_graph()
        initial_state = {
            "raw_input": "Warfarin 5mg once daily, Aspirin 81mg once daily",
            "input_type": "text",
            "drugs": [], "patient_info": {},
            "interactions": [], "contraindications": [],
            "web_findings": [], "severity_score": "SAFE",
            "alternatives": [], "report": {},
            "error": None, "next": "ingestion"
        }

        result = graph.invoke(initial_state)
        report = result.get("report", {})

        self.assertIn("report_id", report, "Report must have an ID")
        self.assertIn("overall_severity", report, "Report must have severity")
        self.assertEqual(report["overall_severity"], "HIGH")
        self.assertEqual(len(report["drugs_analyzed"]), 2)
        self.assertTrue(len(report["interactions"]) > 0)
        self.assertTrue(len(report["alternatives"]) > 0)
        self.assertIn("disclaimer", report)
        self.assertEqual(report["urgency"], "URGENT")
        print(f"\nFull pipeline test passed | Report ID: {report.get('report_id')}")


if __name__ == "__main__":
    print("=" * 60)
    print("  Drug Interaction Checker — Test Suite")
    print("=" * 60)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for cls in [
        TestDrugAPITools,
        TestPubMedTool,
        TestGraphState,
        TestSupervisor,
        TestAggregator,
        TestIngestionAgent,
        TestContraindicationAgent,
        TestAlternativesAgent,
        TestReportAgent,
        TestFullGraphMocked,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
