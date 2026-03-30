import os
import re
import sys
import html
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import json
import tempfile

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RxCheck · Drug Interaction Checker",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;1,9..144,300&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:        #fafaf8;
  --surface:   #ffffff;
  --surface2:  #f5f4f0;
  --ink:        #1a1a18;
  --ink2:       #4a4a45;
  --ink3:       #8a8a82;
  --border:     #e4e2da;
  --border2:    #d0cec5;
  --accent:     #1a5c3a;
  --accent2:    #2d7a52;
  --accent-bg:  #eef6f1;
  --red:        #9b2335;
  --red-bg:     #fdf1f3;
  --amber:      #8a5200;
  --amber-bg:   #fdf6e7;
  --blue:       #1a3c6e;
  --blue-bg:    #eff4fc;
  --radius:     12px;
  --radius-sm:  8px;
  --shadow:     0 1px 3px rgba(26,26,24,0.06), 0 4px 16px rgba(26,26,24,0.04);
  --shadow-md:  0 2px 8px rgba(26,26,24,0.08), 0 12px 32px rgba(26,26,24,0.06);
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
  color: var(--ink);
}

.stApp { background: var(--bg); }

/* ── Hide chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2rem 4rem; max-width: 1060px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--surface);
  border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] > div { padding: 1.5rem 1.25rem; }
section[data-testid="stSidebar"] * { color: var(--ink) !important; }
section[data-testid="stSidebar"] .stTextArea textarea,
section[data-testid="stSidebar"] .stNumberInput input {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm);
  font-size: 13px !important;
  color: var(--ink) !important;
}
section[data-testid="stSidebar"] .stTextArea textarea:focus,
section[data-testid="stSidebar"] .stNumberInput input:focus {
  border-color: var(--accent2) !important;
  box-shadow: 0 0 0 3px rgba(45,122,82,0.12) !important;
}
section[data-testid="stSidebar"] hr { border-color: var(--border); margin: 1rem 0; }

/* ── Sidebar sample buttons ── */
section[data-testid="stSidebar"] .stButton > button {
  background: var(--surface2) !important;
  color: var(--ink2) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  padding: 6px 12px !important;
  transition: all 0.15s !important;
  text-align: left !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: var(--accent-bg) !important;
  border-color: var(--accent2) !important;
  color: var(--accent) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  gap: 2px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 3px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px;
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--ink3);
  background: transparent;
  border: none;
  transition: all 0.15s;
}
.stTabs [aria-selected="true"] {
  background: var(--surface) !important;
  color: var(--ink) !important;
  font-weight: 600 !important;
  box-shadow: var(--shadow) !important;
}

/* ── Main text area ── */
.stTextArea textarea {
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--ink);
  font-size: 14px;
  line-height: 1.65;
  font-family: 'DM Sans', sans-serif;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.stTextArea textarea:focus {
  border-color: var(--accent2) !important;
  box-shadow: 0 0 0 3px rgba(45,122,82,0.12) !important;
}
.stTextArea textarea::placeholder { color: var(--ink3); }

/* ── File uploader ── */
.stFileUploader section {
  background: var(--surface);
  border: 1.5px dashed var(--border2);
  border-radius: var(--radius);
  transition: border-color 0.15s;
}
.stFileUploader section:hover { border-color: var(--accent2); }

/* ── Primary analyze button ── */
.stButton > button[kind="primary"] {
  background: var(--accent) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  font-size: 14px !important;
  letter-spacing: 0.01em !important;
  padding: 12px 0 !important;
  transition: all 0.2s !important;
  box-shadow: 0 1px 3px rgba(26,92,58,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--accent2) !important;
  box-shadow: 0 4px 12px rgba(26,92,58,0.35) !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

/* ── Download button ── */
.stDownloadButton > button {
  background: var(--surface) !important;
  color: var(--ink2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  transition: all 0.15s !important;
}
.stDownloadButton > button:hover {
  border-color: var(--ink2) !important;
  color: var(--ink) !important;
  background: var(--surface2) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Custom card components ── */
.rx-header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
}
.rx-wordmark {
  font-family: 'Fraunces', serif;
  font-size: 20px;
  font-weight: 400;
  color: var(--ink);
  letter-spacing: -0.02em;
}
.rx-wordmark span { color: var(--accent); }

.rx-page-title {
  font-family: 'Fraunces', serif;
  font-size: 36px;
  font-weight: 300;
  color: var(--ink);
  letter-spacing: -0.03em;
  line-height: 1.15;
  margin: 0 0 6px;
}
.rx-page-sub {
  font-size: 14px;
  color: var(--ink3);
  font-weight: 400;
  line-height: 1.5;
}

/* ── Severity pills ── */
.pill {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 999px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.06em;
  text-transform: uppercase; font-family: 'DM Sans', sans-serif;
}
.pill-safe     { background: #e6f4ec; color: #14532d; }
.pill-low      { background: #fef9c3; color: #713f12; }
.pill-moderate { background: #fdf3e0; color: #8a5200; }
.pill-high     { background: #fce8eb; color: #9b2335; }
.pill-critical { background: #fce8eb; color: #7f1d1d; }

/* ── Drug chip ── */
.drug-chip {
  display: inline-flex; align-items: center; gap: 4px;
  background: var(--surface2); color: var(--ink2);
  border: 1px solid var(--border);
  padding: 3px 11px; border-radius: 999px;
  font-size: 12px; font-weight: 500; margin: 2px;
  letter-spacing: 0.01em;
}

/* ── Metric boxes ── */
.metric-strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  margin-bottom: 28px;
}
.metric-box {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 14px 16px;
  box-shadow: var(--shadow);
}
.metric-box .mlabel {
  font-size: 10px; color: var(--ink3);
  font-weight: 600; letter-spacing: 0.08em;
  text-transform: uppercase; margin-bottom: 8px;
}
.metric-box .mval {
  font-family: 'Fraunces', serif;
  font-size: 24px; font-weight: 400;
  color: var(--ink); line-height: 1;
}

/* ── Section label ── */
.sec-label {
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--ink3); margin-bottom: 10px;
}

/* ── Info card ── */
.rx-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 22px;
  margin-bottom: 12px;
  box-shadow: var(--shadow);
}
.rx-card.danger  { border-left: 3px solid var(--red);   background: var(--red-bg); }
.rx-card.warning { border-left: 3px solid #c97b00;      background: var(--amber-bg); }
.rx-card.success { border-left: 3px solid var(--accent); background: var(--accent-bg); }
.rx-card.info    { border-left: 3px solid var(--blue);   background: var(--blue-bg); }

/* ── Interaction rows ── */
.ix-item {
  display: flex; gap: 16px; align-items: flex-start;
  padding: 16px 0; border-bottom: 1px solid var(--border);
}
.ix-item:last-child { border-bottom: none; padding-bottom: 0; }
.ix-pill-col { min-width: 90px; padding-top: 1px; }
.ix-body {}
.ix-drugs {
  font-weight: 600; font-size: 14px; color: var(--ink);
  margin-bottom: 4px;
}
.ix-arrow { color: var(--ink3); font-weight: 400; margin: 0 4px; }
.ix-desc  { font-size: 13px; color: var(--ink2); line-height: 1.55; }
.ix-rec   { font-size: 12px; color: var(--ink3); margin-top: 6px; }
.ix-src   { font-size: 11px; color: var(--border2); margin-top: 3px; letter-spacing: 0.02em; }

/* ── Alternative cards ── */
.alt-block {
  background: var(--accent-bg);
  border: 1px solid #c4dfd0;
  border-radius: 10px;
  padding: 13px 16px;
  margin-top: 10px;
}
.alt-name  { font-weight: 600; font-size: 14px; color: var(--accent); }
.alt-class { font-size: 12px; color: var(--ink3); font-weight: 400; margin-left: 6px; }
.alt-rat   { font-size: 13px; color: var(--ink2); margin-top: 4px; line-height: 1.5; }
.alt-note  { font-size: 12px; color: var(--ink3); margin-top: 5px; }

/* ── Tip box ── */
.tip-box {
  background: var(--blue-bg);
  border: 1px solid #c8d9f0;
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  font-size: 12px;
  color: var(--blue);
  margin-bottom: 14px;
  line-height: 1.6;
}

/* ── Sidebar label ── */
.sb-label {
  font-size: 10px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--ink3); margin-bottom: 10px; display: block;
}

/* ── Status badge (URGENT / ROUTINE) ── */
.status-badge {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 12px; border-radius: 999px;
  font-size: 11px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
}
.status-emergency { background: #fce8eb; color: #9b2335; }
.status-urgent    { background: #fdf3e0; color: #8a5200; }
.status-routine   { background: #e6f4ec; color: #14532d; }

/* ── Divider ── */
.rx-divider {
  border: none; border-top: 1px solid var(--border); margin: 28px 0;
}

/* ── Report header ── */
.report-meta {
  font-size: 11px; color: var(--ink3); letter-spacing: 0.02em;
}

/* Expander */
[data-testid="stExpander"] {
  background: var(--surface);
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  box-shadow: var(--shadow);
}

/* Number input */
.stNumberInput input {
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  font-size: 14px;
}
.stNumberInput input:focus {
  border-color: var(--accent2) !important;
  box-shadow: 0 0 0 3px rgba(45,122,82,0.12) !important;
}

/* Caption */
.stCaption { color: var(--ink3); font-size: 12px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def pill(sev: str) -> str:
    s = (sev or "SAFE").upper()
    c = {"SAFE":"safe","LOW":"low","MODERATE":"moderate","HIGH":"high",
         "CRITICAL":"critical","CONTRAINDICATED":"critical"}.get(s, "low")
    icons = {"safe":"●","low":"●","moderate":"●","high":"●","critical":"●"}
    return f'<span class="pill pill-{c}">{icons.get(c,"●")} {s}</span>'


def chips(names: list) -> str:
    return " ".join(f'<span class="drug-chip">⬡ {n.title()}</span>' for n in names)


def status_badge(urg: str) -> str:
    urg = (urg or "ROUTINE").upper()
    cls = {"EMERGENCY":"emergency","URGENT":"urgent","ROUTINE":"routine"}.get(urg,"routine")
    icons = {"emergency":"⚠", "urgent":"!", "routine":"✓"}
    return f'<span class="status-badge status-{cls}">{icons.get(cls,"●")} {urg}</span>'


def sanitize_model_text(value) -> str:
    if value is None:
        return ""

    text = str(value)
    # Remove markdown code fences and any embedded HTML so model artifacts show as plain prose.
    text = re.sub(r"```[a-zA-Z0-9_-]*", "", text)
    text = text.replace("```", "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return html.escape(text)


def normalize_alternatives_items(items):
    if isinstance(items, list):
        return [item for item in items if isinstance(item, dict)]
    if isinstance(items, dict):
        return [items]
    if isinstance(items, str) and items.strip():
        return [{"name": "", "class": "", "rationale": items, "notes": ""}]
    return []


def run_check(raw_input: str, input_type: str, patient_info: dict) -> dict:
    initial_state = {
        "raw_input": raw_input, "input_type": input_type,
        "drugs": [], "patient_info": patient_info,
        "interactions": [], "contraindications": [],
        "web_findings": [], "severity_score": "SAFE",
        "alternatives": [], "report": {},
        "error": None, "next": "ingestion",
        "parallel_checks_complete": False,
        "alternatives_complete": False,
    }
    result = st.session_state.graph.invoke(initial_state)
    return result.get("report", {})


def render_report(report: dict):
    if not report:
        st.warning("No report was generated.")
        return

    sev    = report.get("overall_severity", "SAFE")
    urg    = report.get("urgency", "ROUTINE")
    drugs  = report.get("drugs_analyzed", [])
    ixs    = report.get("interactions", [])
    cis    = report.get("contraindications", [])
    alts   = report.get("alternatives", [])
    web    = report.get("web_findings", [])
    summ   = report.get("clinical_summary", "")
    recs   = report.get("key_recommendations", [])
    rep_id = report.get("report_id", "")
    gen_at = report.get("generated_at", "")[:19].replace("T", " ")

    # ── Header row ────────────────────────────────────────────────────────────
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(
            f'<p class="report-meta">Report <strong>{rep_id}</strong> &nbsp;·&nbsp; {gen_at}</p>',
            unsafe_allow_html=True
        )
    with c2:
        st.download_button(
            "↓ Export JSON",
            data=json.dumps(report, indent=2),
            file_name=f"rxcheck_{rep_id}.json",
            mime="application/json",
            use_container_width=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Metric strip ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-strip">
      <div class="metric-box">
        <div class="mlabel">Severity</div>
        <div>{pill(sev)}</div>
      </div>
      <div class="metric-box">
        <div class="mlabel">Urgency</div>
        <div>{status_badge(urg)}</div>
      </div>
      <div class="metric-box">
        <div class="mlabel">Interactions</div>
        <div class="mval">{len(ixs)}</div>
      </div>
      <div class="metric-box">
        <div class="mlabel">Contraindications</div>
        <div class="mval">{len(cis)}</div>
      </div>
      <div class="metric-box">
        <div class="mlabel">Drugs</div>
        <div class="mval">{len(drugs)}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Drug chips ────────────────────────────────────────────────────────────
    if drugs:
        st.markdown(chips(drugs) + "<div style='height:22px'></div>", unsafe_allow_html=True)

    # ── Clinical summary ──────────────────────────────────────────────────────
    if summ:
        st.markdown('<p class="sec-label">Clinical Summary</p>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="rx-card info" style="font-size:14px;line-height:1.7;color:#1a3c6e">{summ}</div>',
            unsafe_allow_html=True
        )

    # ── Recommendations ───────────────────────────────────────────────────────
    if recs:
        st.markdown('<p class="sec-label">Key Recommendations</p>', unsafe_allow_html=True)
        items_html = "".join(
            f"<li style='margin-bottom:7px;font-size:13px;color:#1a3256;line-height:1.55'>{r}</li>"
            for r in recs
        )
        st.markdown(
            f'<div class="rx-card success"><ul style="margin:0;padding-left:18px">{items_html}</ul></div>',
            unsafe_allow_html=True
        )

    # ── Interactions ──────────────────────────────────────────────────────────
    st.markdown('<p class="sec-label">Drug Interactions</p>', unsafe_allow_html=True)
    if ixs:
        has_high = any(i.get("severity","").upper() in ("HIGH","CRITICAL","CONTRAINDICATED") for i in ixs)
        card_cls = "danger" if has_high else "warning"
        rows_html = ""
        for ix in ixs:
            rows_html += f"""
            <div class="ix-item">
              <div class="ix-pill-col">{pill(ix.get('severity','LOW'))}</div>
              <div class="ix-body">
                <div class="ix-drugs">
                  {ix.get('drug1','?').title()}
                  <span class="ix-arrow">↔</span>
                  {ix.get('drug2','?').title()}
                </div>
                <div class="ix-desc">{ix.get('description','')}</div>
                <div class="ix-rec">→ {ix.get('recommendation','')}</div>
                <div class="ix-src">{ix.get('source','')}</div>
              </div>
            </div>"""
        st.markdown(f'<div class="rx-card {card_cls}">{rows_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="rx-card success" style="font-size:14px;color:#14532d;font-weight:500">'
            '✓ &nbsp;No drug–drug interactions detected.</div>',
            unsafe_allow_html=True
        )

    # ── Contraindications ─────────────────────────────────────────────────────
    if cis:
        st.markdown('<p class="sec-label">Contraindications</p>', unsafe_allow_html=True)
        rows_html = ""
        for ci in cis:
            rows_html += f"""
            <div class="ix-item">
              <div class="ix-pill-col">{pill(ci.get('severity','HIGH'))}</div>
              <div class="ix-body">
                <div class="ix-drugs">
                  {ci.get('drug','?').title()}
                  <span style="font-weight:400;color:#4a4a45;margin:0 4px">—</span>
                  {ci.get('condition','')}
                </div>
                <div class="ix-desc">{ci.get('description','')}</div>
                <div class="ix-rec">→ {ci.get('recommendation','')}</div>
              </div>
            </div>"""
        st.markdown(f'<div class="rx-card danger">{rows_html}</div>', unsafe_allow_html=True)

    # ── Alternatives ──────────────────────────────────────────────────────────
    if alts:
        st.markdown('<p class="sec-label">Suggested Alternatives</p>', unsafe_allow_html=True)
        for alt in alts:
            if not isinstance(alt, dict):
                continue
            original_drug = sanitize_model_text(alt.get("original_drug", "")).title()
            reason_for_change = sanitize_model_text(alt.get("reason_for_change", ""))

            with st.container(border=True):
                if original_drug:
                    st.markdown(f"**{original_drug}**")
                if reason_for_change:
                    st.write(reason_for_change)

                for a in normalize_alternatives_items(alt.get("alternatives", [])):
                    alt_name = sanitize_model_text(a.get("name", "")).title()
                    alt_class = sanitize_model_text(a.get("class", ""))
                    alt_rationale = sanitize_model_text(a.get("rationale", ""))
                    alt_notes = sanitize_model_text(a.get("notes", ""))

                    line = alt_name or "Alternative"
                    if alt_class:
                        line = f"{line} ({alt_class})"
                    st.markdown(f"- **{line}**")
                    if alt_rationale:
                        st.write(alt_rationale)
                    if alt_notes:
                        st.caption(alt_notes)

    # ── Literature findings ───────────────────────────────────────────────────
    if web:
        with st.expander(f"Literature & Adverse Event Findings  ({len(web)})", expanded=False):
            for wf in web:
                sig = wf.get("clinical_significance", "LOW")
                drugs_str = ", ".join(wf.get("drugs_involved", []))
                st.markdown(f"""
                <div style="padding:12px 0;border-bottom:1px solid var(--border)">
                  <div style="font-size:14px;font-weight:500;color:var(--ink);margin-bottom:5px">
                    {wf.get('finding','')}
                  </div>
                  <div style="font-size:12px;color:var(--ink3);display:flex;gap:12px;align-items:center">
                    <span>{drugs_str}</span>
                    <span>·</span>
                    {pill(sig)}
                    <span>·</span>
                    <span>{wf.get('source','')}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

    # ── Disclaimer ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.caption(f"⚕ {report.get('disclaimer','')}")


# ── Session state ─────────────────────────────────────────────────────────────
if "graph" not in st.session_state:
    with st.spinner("Initialising pipeline…"):
        from graph.builder import build_graph
        st.session_state.graph = build_graph()

if "report" not in st.session_state:
  st.session_state.report = None

if "sample_text" not in st.session_state:
  st.session_state.sample_text = ""


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Wordmark
    st.markdown("""
    <div style="padding:4px 0 20px">
      <div style="font-family:'Fraunces',serif;font-size:22px;font-weight:400;
                  letter-spacing:-0.03em;color:#1a1a18">
        Rx<span style="color:#1a5c3a">Check</span>
      </div>
      <div style="font-size:11px;color:#8a8a82;margin-top:3px;font-weight:400">
        Drug Interaction Intelligence
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Patient info
    st.markdown('<span class="sb-label">Patient (optional)</span>', unsafe_allow_html=True)
    patient_age = st.number_input("Age", min_value=0, max_value=120, value=0, step=1)
    patient_conditions = st.text_area(
        "Conditions", placeholder="Type 2 diabetes\nHypertension\nRenal impairment",
        height=80
    )
    patient_allergies = st.text_area(
        "Allergies", placeholder="Penicillin\nSulfa drugs",
        height=68
    )

    st.markdown("---")

    # Quick examples
    st.markdown('<span class="sb-label">Quick examples</span>', unsafe_allow_html=True)
    samples = {
        "Warfarin + Aspirin":  "Warfarin 5mg once daily, Aspirin 81mg once daily, Omeprazole 20mg OD",
        "Serotonin risk":      "Sertraline 50mg OD, Tramadol 50mg TID PRN",
        "Polypharmacy":        "Warfarin 5mg, Aspirin 81mg, Ibuprofen 400mg TID, Fluoxetine 20mg OD",
        "Safe combination":    "Amlodipine 5mg OD, Atorvastatin 40mg OD, Ramipril 5mg OD",
    }
    for label, text in samples.items():
        if st.button(label, use_container_width=True, key=f"s_{label}"):
            st.session_state.sample_text = text
            st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="font-size:11px;color:#8a8a82;line-height:1.6">'
        'Powered by <strong>LangGraph</strong> · <strong>Ollama</strong><br>'
        'Free · local · open source'
        '</div>',
        unsafe_allow_html=True
    )


# ── Main ──────────────────────────────────────────────────────────────────────
patient_info = {
    "age":        int(patient_age) if patient_age else None,
    "conditions": [c.strip() for c in patient_conditions.splitlines() if c.strip()],
    "allergies":  [a.strip() for a in patient_allergies.splitlines()  if a.strip()],
}

# Page title
st.markdown("""
<div style="margin-bottom:32px">
  <h1 class="rx-page-title">Drug Interaction<br>Checker</h1>
  <p class="rx-page-sub">
    Enter a prescription, upload a PDF, or photograph a label —<br>
    the multi-agent pipeline checks interactions, contraindications, and suggests alternatives.
  </p>
</div>
""", unsafe_allow_html=True)

# Input tabs
tab_text, tab_pdf, tab_img = st.tabs(["✏  Text", "  PDF", "◧  Image"])

with tab_text:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    prescription_text = st.text_area(
        "prescription",
        value=st.session_state.sample_text,
        height=130,
        placeholder="e.g.  Warfarin 5mg once daily,  Aspirin 81mg OD,  Metformin 500mg BD",
        label_visibility="collapsed",
    )
    if st.button("Analyse prescription  →", type="primary", use_container_width=True, key="btn_t"):
        if not prescription_text.strip():
            st.warning("Please enter a prescription.")
        else:
            with st.spinner("Running analysis…"):
                try:
                    st.session_state.report = run_check(prescription_text, "text", patient_info)
                except Exception as e:
                    st.error(f"Error: {e}")

with tab_pdf:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    up_pdf = st.file_uploader("pdf", type=["pdf"], label_visibility="collapsed")
    if st.button("Analyse PDF  →", type="primary", use_container_width=True, key="btn_p"):
        if not up_pdf:
            st.warning("Please upload a PDF.")
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(up_pdf.read())
                path = tmp.name
            with st.spinner("Extracting text and analysing…"):
                try:
                    st.session_state.report = run_check(path, "pdf", patient_info)
                    os.unlink(path)
                except Exception as e:
                  try:
                    os.unlink(path)
                  except Exception:
                    pass
                    st.error(f"Error: {e}")

with tab_img:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="tip-box">
      <strong>Tip</strong> — use a sharp, well-lit photo of the label.
      Tesseract OCR runs first; if it finds fewer than 20 characters a vision model
      (<code>llama3.2-vision</code> or <code>llava</code>) is tried automatically.
    </div>
    """, unsafe_allow_html=True)
    up_img = st.file_uploader("image", type=["png","jpg","jpeg","tiff","bmp"],
                               label_visibility="collapsed")
    if up_img:
        st.image(up_img, width=300)
    if st.button("Analyse image  →", type="primary", use_container_width=True, key="btn_i"):
        if not up_img:
            st.warning("Please upload an image.")
        else:
            ext = os.path.splitext(up_img.name)[1] or ".png"
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(up_img.read())
                path = tmp.name
            with st.spinner("OCR → vision model → analysis…"):
                try:
                    st.session_state.report = run_check(path, "image", patient_info)
                    os.unlink(path)
                except Exception as e:
                  try:
                    os.unlink(path)
                  except Exception:
                    pass
                    st.error(f"Error: {e}")

# ── Report output ──────────────────────────────────────────────────────────────
if st.session_state.report:
    st.markdown("<hr class='rx-divider'>", unsafe_allow_html=True)
    report = st.session_state.report
    err = report.get("error") if isinstance(report, dict) else None
    if err:
        st.error(f"⚠ {err}")
    else:
        render_report(report)