#!/usr/bin/env python3
"""
CLI runner for Drug Interaction Checker.
Usage: python run.py "Warfarin 5mg, Aspirin 100mg, Omeprazole 20mg"
"""
import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

SEVERITY_COLORS = {
    "SAFE": "green",
    "LOW": "yellow",
    "MODERATE": "dark_orange",
    "HIGH": "red",
    "CRITICAL": "bold red",
    "CONTRAINDICATED": "bold red",
}


def color_severity(sev: str) -> Text:
    sev = (sev or "SAFE").upper()
    color = SEVERITY_COLORS.get(sev, "white")
    return Text(sev, style=color)


def print_report(report: dict):
    console.print()
    console.rule("[bold blue]Drug Interaction Report[/bold blue]")

    console.print(f"[dim]Report ID:[/dim] {report.get('report_id','N/A')}")
    console.print(f"[dim]Generated:[/dim] {report.get('generated_at','')[:19].replace('T',' ')}")
    console.print()

    sev = report.get("overall_severity", "SAFE")
    urg = report.get("urgency", "ROUTINE")
    sev_color = SEVERITY_COLORS.get(sev, "white")
    console.print(Panel(
        f"Overall Severity: [{sev_color}]{sev}[/{sev_color}]   |   Urgency: {urg}",
        title="Assessment",
        border_style="blue"
    ))

    drugs = report.get("drugs_analyzed", [])
    if drugs:
        console.print(f"\n[bold]Drugs analyzed:[/bold] {', '.join(d.title() for d in drugs)}")

    summary = report.get("clinical_summary", "")
    if summary:
        console.print(Panel(summary, title="[bold]Clinical Summary[/bold]", border_style="dim"))

    recs = report.get("key_recommendations", [])
    if recs:
        console.print("\n[bold green]Key Recommendations:[/bold green]")
        for rec in recs:
            console.print(f"  - {rec}")

    interactions = report.get("interactions", [])
    if interactions:
        console.print(f"\n[bold yellow]Drug Interactions ({len(interactions)} found):[/bold yellow]")
        tbl = Table(box=box.ROUNDED, show_header=True, header_style="bold")
        tbl.add_column("Drug 1", style="cyan")
        tbl.add_column("Drug 2", style="cyan")
        tbl.add_column("Severity", justify="center")
        tbl.add_column("Description", max_width=50)
        for ix in interactions:
            tbl.add_row(
                ix.get("drug1", "?").title(),
                ix.get("drug2", "?").title(),
                color_severity(ix.get("severity", "LOW")),
                ix.get("description", "")[:100]
            )
        console.print(tbl)
    else:
        console.print("\n[green]No drug-drug interactions detected.[/green]")

    contraindications = report.get("contraindications", [])
    if contraindications:
        console.print(f"\n[bold red] Contraindications ({len(contraindications)} found):[/bold red]")
        for ci in contraindications:
            console.print(Panel(
                f"[bold]{ci.get('drug','?').title()}[/bold] — {ci.get('condition','?')}\n"
                f"{ci.get('description','')}\n"
                f"[dim]Recommendation: {ci.get('recommendation','')}[/dim]",
                border_style="red"
            ))

    alternatives = report.get("alternatives", [])
    if alternatives:
        console.print(f"\n[bold cyan]Suggested Alternatives:[/bold cyan]")
        for alt in alternatives:
            console.print(f"\n  [bold]{alt.get('original_drug','?').title()}[/bold] — {alt.get('reason_for_change','')}")
            for a in alt.get("alternatives", []):
                console.print(f"    - {a.get('name','?').title()} ({a.get('class','')})")
                console.print(f"      {a.get('rationale','')}")

    console.print()
    console.print(Panel(
        f"[dim]{report.get('disclaimer','')}[/dim]",
        border_style="dim", title="Disclaimer"
    ))


def main():
    parser = argparse.ArgumentParser(description="Drug Interaction Checker CLI")
    parser.add_argument("prescription", nargs="?", help="Prescription text (or use --file)")
    parser.add_argument("--file", help="Path to prescription PDF or image")
    parser.add_argument("--age", type=int, help="Patient age")
    parser.add_argument("--conditions", nargs="*", default=[], help="Patient conditions")
    parser.add_argument("--allergies", nargs="*", default=[], help="Patient allergies")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if not args.prescription and not args.file:
        console.print("[red]Error:[/red] Provide prescription text or --file path")
        parser.print_help()
        sys.exit(1)

    console.print("[bold blue]Loading Drug Interaction Checker…[/bold blue]")
    from graph.builder import build_graph
    graph = build_graph()

    if args.file:
        raw_input = args.file
        ext = os.path.splitext(args.file)[1].lower()
        input_type = "pdf" if ext == ".pdf" else "image"
    else:
        raw_input = args.prescription
        input_type = "text"

    patient_info = {
        "age": args.age,
        "conditions": args.conditions,
        "allergies": args.allergies,
    }

    console.print(f"[dim]Analyzing {input_type} input through multi-agent pipeline…[/dim]")

    initial_state = {
        "raw_input": raw_input,
        "input_type": input_type,
        "drugs": [], "patient_info": patient_info,
        "interactions": [], "contraindications": [],
        "web_findings": [], "severity_score": "SAFE",
        "alternatives": [], "report": {},
        "error": None, "next": "ingestion"
    }

    result = graph.invoke(initial_state)
    report = result.get("report", {})

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
