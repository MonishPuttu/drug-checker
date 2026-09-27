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

## Voice-over version (43s)
The final `brag.mp4` is the extended cut with narration. Voice: Kokoro TTS (`af_heart`), generated locally. Each scene's timeline was stretched to fit its line (entrances and transitions keep their original speed; only the hold in the middle of each scene slows down), the soundtrack was re-timed to match, and the music ducks under the voice. Some spellings below are written for the voice, e.g. "Ani-Talk", "R-x Check".

| # | Time | Narration |
|---|------|-----------|
| 1 | 0.0–3.5s | A routine prescription. But is it safe? |
| 2 | 3.5–9.5s | R-x Check is an AI safety checker that reviews a prescription before it's dispensed. |
| 3 | 9.5–21.0s | Six specialised agents, orchestrated by Lang Graph, check interactions against R-x Norm and Open F-D-A, flag contraindications, and suggest safer alternatives. |
| 4 | 21.0–30.4s | The result is a clear clinical report. Here, warfarin with aspirin is flagged high severity for bleeding risk, with recommendations to follow up. |
| 5 | 30.4–36.8s | Type it, upload a PDF, or snap a photo of the label. It all runs locally, with Ollama. |
| 6 | 36.8–42.9s | R-x Check. Check before it's dispensed. It's open source on GitHub. |
