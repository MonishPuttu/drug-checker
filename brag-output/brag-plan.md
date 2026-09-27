# /brag plan — drug-checker (RxCheck)

**What it is:** RxCheck — an AI multi-agent prescription safety checker. Paste a prescription (or upload a PDF / photo of a label) and a LangGraph pipeline checks drug interactions, contraindications and safer alternatives, then writes a clinical report — running locally on Llama 3.2 via Ollama.
**Who it's for:** Pharmacists, clinicians and students who want a second check before a prescription is dispensed.
**What sets it apart:** Six specialised agents (ingestion, interaction, contraindication, web search, alternatives, report) orchestrated by a LangGraph supervisor, grounded in RxNorm / OpenFDA / PubMed, and 100% local.
**Most impressive claim:** It catches a HIGH-severity interaction in a routine three-drug prescription.
**Visual hook:** "A routine prescription." → the red "HIGH severity detected" banner.
**Tone:** polished — calm, clinical, cream-and-ink.
**Share caption:** "Check before it's dispensed. Every time."

## Visual identity (from the code)
- Palette, type and copy from `ui/app.py`: cream `#f7f5f0`, ink `#18181a`, red/amber/green/blue severity tokens, Instrument Serif + Geist, "Check before it's dispensed. Every time.", "Free · local · open source · LangGraph + Ollama"
- Results layout (Parsed → Interactions → Severity → Report steps, severity banner, Clinical Summary, Key Recommendations, interaction cards, HIGH / URGENT pills) rebuilt from `screen_results()`
- Agent graph from the README architecture and `agents/`, `graph/`
- Example prescription "Warfarin 5mg OD, Aspirin 81mg OD, Omeprazole 20mg OD" is the app's own "Warfarin + Aspirin" quick example

## Honesty note
The live pipeline could not be run here: it needs a local Ollama model, and this environment's network policy blocks RxNorm / OpenFDA / PubMed. The report on screen is an **illustrative** example in the app's exact report schema, limited to well-established facts (warfarin + aspirin → increased bleeding risk; omeprazole may raise INR), and it's labelled "Illustrative report · informational only, not medical advice" in the video.

## Storyboard (21s, 1920×1080 @ 30fps)
| # | Time | Scene | On screen |
|---|------|-------|-----------|
| 1 | 0.0–3.5 | **Hook** | "A routine prescription." typed → Analyse → "⚠ HIGH severity detected · 2 interactions" |
| 2 | 3.5–6.7 | **Reveal** | RxCheck nav + "Check before it's dispensed. Every time." + subline |
| 3 | 6.7–11.2 | **Agents** | "Six agents. One graph." — the LangGraph pipeline lights up level by level |
| 4 | 11.2–15.8 | **Report** | The results screen: steps, banner, clinical summary, recommendations, interaction cards |
| 5 | 15.8–18.5 | **Inputs** | "Text, PDF, or a photo of the label." + "100% local — Ollama" |
| 6 | 18.5–21.0 | **Outro** | RxCheck + GitHub link + "Informational only — not medical advice." |
