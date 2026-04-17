import os, sys, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st

st.set_page_config(page_title="RxCheck", page_icon="⚕", layout="wide",
                   initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital,wght@0,400;1,400&family=Geist:wght@300;400;500;600&display=swap');

:root {
  --cream:#f7f5f0; --white:#ffffff;
  --ink:#18181a; --ink2:#52525b; --ink3:#a1a1aa;
  --border:#e4e4e7; --border2:#d4d4d8;
  --green:#166534; --green-m:#16a34a; --green-l:#dcfce7; --green-b:#f0fdf4;
  --red:#991b1b; --red-m:#dc2626; --red-l:#fee2e2; --red-b:#fff1f2;
  --amber:#92400e; --amber-m:#d97706; --amber-l:#fde68a; --amber-b:#fffbeb;
  --blue:#1e3a8a; --blue-l:#dbeafe; --blue-b:#eff6ff;
  --ss:0 1px 3px rgba(0,0,0,0.06);
  --sm:0 4px 12px rgba(0,0,0,0.08);
  --r:12px; --rsm:8px; --rxs:6px;
}

/* ── Reset ── */
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Geist',sans-serif;color:var(--ink);}
.stApp{background:var(--cream);min-height:100vh;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0!important;max-width:100%!important;min-width:100%!important;}
.stApp > div > div{gap:0!important;}
section[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important;}

/* ── NAV ── */
.rx-nav{
  position:sticky;top:0;z-index:999;
  background:var(--white);border-bottom:1px solid var(--border);
  height:56px;display:flex;align-items:center;justify-content:space-between;
  padding:0 0 0 48px;width:100%;
}
.rx-logo{display:flex;align-items:center;gap:10px;}
.rx-logo-icon{
  width:28px;height:28px;background:var(--ink);border-radius:7px;
  display:flex;align-items:center;justify-content:center;
  font-size:14px;color:white;flex-shrink:0;
}
.rx-logo-text{font-family:'Instrument Serif',serif;font-size:20px;letter-spacing:-0.02em;color:var(--ink);}
.rx-nav-right{display:flex;align-items:center;gap:0;}

/* ── Landing column backgrounds ── */
/* Left col = white, right col = cream — applied via wrapper divs */
.rx-left-bg{
  background:var(--white);
  border-right:1px solid var(--border);
  min-height:calc(100vh - 56px);
  padding:72px 56px 72px 72px;
}
.rx-right-bg{
  background:var(--cream);
  min-height:calc(100vh - 56px);
  padding:72px 72px 72px 56px;
}

/* ── Hero copy ── */
.rx-eyebrow{font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:var(--ink3);margin-bottom:20px;}
.rx-headline{font-family:'Instrument Serif',serif;font-size:50px;font-weight:400;line-height:1.06;letter-spacing:-0.03em;margin-bottom:20px;color:var(--ink);}
.rx-headline em{font-style:italic;color:var(--ink2);}
.rx-subline{font-size:15px;color:var(--ink2);line-height:1.7;max-width:420px;margin-bottom:40px;}
.rx-features{display:flex;flex-direction:column;gap:14px;}
.rx-feat{display:flex;align-items:flex-start;gap:12px;}
.rx-feat-icon{
  width:20px;height:20px;border-radius:50%;background:var(--green-b);
  border:1px solid var(--green-l);flex-shrink:0;margin-top:1px;
  display:flex;align-items:center;justify-content:center;font-size:10px;color:var(--green);
}
.rx-feat-text{font-size:14px;color:var(--ink2);line-height:1.5;}
.rx-feat-text strong{color:var(--ink);font-weight:600;}
.rx-input-label{font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink3);margin-bottom:16px;}
.rx-ex-label{font-size:11px;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;color:var(--ink3);margin-bottom:8px;margin-top:16px;}

/* ── Result layout ── */
.rx-result-outer{
  display:grid;grid-template-columns:1fr 360px;min-height:calc(100vh - 56px);width:100%;
}
.rx-result-main{background:var(--white);border-right:1px solid var(--border);padding:44px 52px;overflow-y:auto;}
.rx-result-side{background:var(--cream);padding:32px 28px;overflow-y:auto;}
.rx-steps{display:flex;align-items:center;margin-bottom:32px;}
.rx-step{display:flex;align-items:center;flex:1;min-width:0;}
.rx-step-dot{width:22px;height:22px;border-radius:50%;background:var(--ink);display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.rx-step-num{color:white;font-size:10px;font-weight:700;}
.rx-step-lbl{font-size:11px;font-weight:600;color:var(--ink);margin-left:8px;white-space:nowrap;}
.rx-step-line{flex:1;height:1px;background:var(--border);margin:0 10px;min-width:6px;}
.rx-banner{border-radius:var(--r);padding:16px 20px;margin-bottom:24px;display:flex;align-items:center;justify-content:space-between;gap:16px;}
.rx-sec{font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink3);margin-bottom:12px;font-family:'Geist',sans-serif;}
.rx-card{background:#ffffff;border:1px solid var(--border);border-radius:var(--r);padding:16px 18px;margin-bottom:10px;box-shadow:var(--ss);}
.rx-panel-card{background:var(--white);border:1px solid var(--border);border-radius:var(--rsm);padding:14px 16px;margin-bottom:12px;box-shadow:var(--ss);}
.rx-panel-title{font-size:10px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--ink3);margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--border);}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{gap:2px!important;background:#eeede9!important;border:1px solid var(--border2)!important;border-radius:var(--rsm)!important;padding:3px!important;display:inline-flex!important;width:auto!important;}
.stTabs [data-baseweb="tab"]{border-radius:var(--rxs)!important;padding:7px 18px!important;font-size:13px!important;font-weight:500!important;color:var(--ink2)!important;background:transparent!important;border:none!important;font-family:'Geist',sans-serif!important;height:32px!important;min-height:unset!important;}
.stTabs [aria-selected="true"]{background:var(--white)!important;color:var(--ink)!important;font-weight:600!important;box-shadow:var(--ss)!important;}
[data-testid="stTabContent"]{padding-top:0!important;}

/* ── Textarea ── */
.stTextArea label{display:none!important;}
.stTextArea textarea{border-radius:var(--rsm)!important;border:1.5px solid var(--border)!important;background:var(--white)!important;color:var(--ink)!important;font-size:15px!important;line-height:1.7!important;font-family:'Geist',sans-serif!important;padding:14px 16px!important;box-shadow:var(--ss)!important;resize:none!important;transition:border-color 0.15s,box-shadow 0.15s!important;}
.stTextArea textarea:focus{border-color:var(--green-m)!important;box-shadow:0 0 0 3px rgba(22,163,74,0.12)!important;outline:none!important;}
.stTextArea textarea::placeholder{color:var(--ink3)!important;}

/* ── File uploader ── */
.stFileUploader label{display:none!important;}
.stFileUploader [data-testid="stFileUploadDropzone"]{background:var(--white)!important;border:1.5px dashed var(--border2)!important;border-radius:var(--r)!important;box-shadow:var(--ss)!important;}
.stFileUploader [data-testid="stFileUploadDropzone"]:hover{border-color:var(--green-m)!important;}

/* ── Primary button ── */
.stButton>button[kind="primary"]{background:var(--ink)!important;color:#fff!important;border:none!important;border-radius:var(--rsm)!important;font-weight:600!important;font-size:15px!important;letter-spacing:-0.01em!important;height:48px!important;min-height:48px!important;padding:0!important;font-family:'Geist',sans-serif!important;box-shadow:var(--sm)!important;transition:all 0.15s!important;width:100%!important;}
.stButton>button[kind="primary"]:hover{background:#27272a!important;transform:translateY(-1px)!important;}
.stButton>button[kind="primary"]:active{transform:translateY(0)!important;}

/* ── Example / secondary buttons ── */
div[data-testid="column"] .stButton>button:not([kind="primary"]){height:34px!important;min-height:34px!important;padding:0 10px!important;font-size:12px!important;font-weight:500!important;line-height:1!important;border-radius:var(--rxs)!important;background:var(--white)!important;color:var(--ink2)!important;border:1px solid var(--border)!important;box-shadow:var(--ss)!important;white-space:nowrap!important;font-family:'Geist',sans-serif!important;transition:all 0.12s!important;}
div[data-testid="column"] .stButton>button:not([kind="primary"]):hover{border-color:var(--border2)!important;color:var(--ink)!important;background:#fafaf8!important;}

/* ── Back button ── */
.rx-back .stButton>button:not([kind="primary"]){height:36px!important;min-height:36px!important;padding:0 16px!important;font-size:13px!important;font-weight:500!important;border-radius:var(--rxs)!important;background:transparent!important;color:var(--ink2)!important;border:1px solid var(--border)!important;box-shadow:none!important;font-family:'Geist',sans-serif!important;transition:all 0.12s!important;}
.rx-back .stButton>button:not([kind="primary"]):hover{color:var(--ink)!important;border-color:var(--border2)!important;background:var(--cream)!important;}

/* ── Download button ── */
.stDownloadButton>button{background:var(--white)!important;color:var(--ink2)!important;border:1px solid var(--border)!important;border-radius:var(--rxs)!important;font-size:13px!important;font-weight:500!important;height:36px!important;font-family:'Geist',sans-serif!important;box-shadow:var(--ss)!important;}
.stDownloadButton>button:hover{color:var(--ink)!important;border-color:var(--border2)!important;}

/* ── Number input ── */
.stNumberInput input{border-radius:var(--rsm)!important;border:1.5px solid var(--border)!important;background:var(--white)!important;font-family:'Geist',sans-serif!important;font-size:14px!important;}
.stNumberInput input:focus{border-color:var(--green-m)!important;box-shadow:0 0 0 3px rgba(22,163,74,0.12)!important;}

/* ── Expander ── */
[data-testid="stExpander"]{background:var(--white)!important;border:1px solid var(--border)!important;border-radius:var(--rsm)!important;box-shadow:var(--ss)!important;margin-top:12px!important;}
[data-testid="stExpander"] summary{font-size:13px!important;color:var(--ink2)!important;padding:10px 14px!important;}
[data-testid="stExpander"] [data-testid="stExpanderDetails"]{padding:0 14px 14px!important;}

/* ── Misc ── */
.stSpinner>div{border-top-color:var(--ink)!important;}
.stImage img{border-radius:var(--r);box-shadow:var(--sm);}

/* ── Nuke all Streamlit column gaps ── */
[data-testid="stHorizontalBlock"]{gap:0!important;}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def sev_pill(s):
    s = (s or "SAFE").upper()
    m = {"SAFE":("#dcfce7","#166534"),"LOW":("#fde68a","#92400e"),"MODERATE":("#fffbeb","#92400e"),
         "HIGH":("#fee2e2","#991b1b"),"CRITICAL":("#fee2e2","#991b1b"),"CONTRAINDICATED":("#fee2e2","#991b1b")}
    bg,fg = m.get(s,("#e4e4e7","#52525b"))
    return (f'<span style="display:inline-flex;align-items:center;gap:4px;background:{bg};color:{fg};'
            f'padding:3px 10px;border-radius:999px;font-size:11px;font-weight:700;'
            f'letter-spacing:0.06em;font-family:Geist,sans-serif;white-space:nowrap">● {s}</span>')

def urg_badge(u):
    u = (u or "ROUTINE").upper()
    m = {"EMERGENCY":("#fee2e2","#991b1b","⚠"),"URGENT":("#fde68a","#92400e","!"),"ROUTINE":("#dcfce7","#166534","✓")}
    bg,fg,icon = m.get(u,("#e4e4e7","#52525b","·"))
    return (f'<span style="display:inline-flex;align-items:center;gap:5px;background:{bg};color:{fg};'
            f'padding:4px 12px;border-radius:999px;font-size:11px;font-weight:700;'
            f'letter-spacing:0.06em;font-family:Geist,sans-serif;white-space:nowrap">{icon} {u}</span>')

def drug_chip(name):
    return (f'<span style="display:inline-flex;align-items:center;gap:5px;background:#ffffff;'
            f'color:#52525b;border:1px solid #e4e4e7;padding:4px 12px;border-radius:999px;'
            f'font-size:12px;font-weight:500;font-family:Geist,sans-serif;margin:2px">'
            f'<span style="width:6px;height:6px;border-radius:50%;background:#a1a1aa;flex-shrink:0;display:inline-block"></span>'
            f'{name.title()}</span>')

def lc(s):
    return {"HIGH":"#dc2626","CRITICAL":"#dc2626","CONTRAINDICATED":"#dc2626","MODERATE":"#d97706"}.get(s.upper(),"#d4d4d8")

def run_check(raw_input, input_type, patient_info):
    state = {"raw_input":raw_input,"input_type":input_type,"drugs":[],"patient_info":patient_info,
             "interactions":[],"contraindications":[],"web_findings":[],"severity_score":"SAFE",
             "alternatives":[],"report":{},"error":None,"next":"ingestion",
             "parallel_checks_complete":False,"alternatives_complete":False}
    return st.session_state.graph.invoke(state).get("report",{})


# ── Session ───────────────────────────────────────────────────────────────────
if "graph" not in st.session_state:
    with st.spinner("Warming up pipeline…"):
        from graph.builder import build_graph
        st.session_state.graph = build_graph()
if "report"      not in st.session_state: st.session_state.report      = None
if "sample_text" not in st.session_state: st.session_state.sample_text = ""


# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN A  —  Landing: left copy / right input
# ═══════════════════════════════════════════════════════════════════════════════
def screen_landing():
    # ── Nav ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <nav class="rx-nav">
      <div class="rx-logo">
        <div class="rx-logo-icon">⚕</div>
        <span class="rx-logo-text">RxCheck</span>
      </div>
      <span style="font-size:12px;color:var(--ink3);padding-right:48px">Free · local · open source · LangGraph + Ollama</span>
    </nav>
    """, unsafe_allow_html=True)

    # ── Two-column split using Streamlit columns ───────────────────────────
    col_left, col_right = st.columns([1, 1], gap="small")

    # LEFT: hero copy in white
    with col_left:
        st.markdown("""
        <div class="rx-left-bg">
          <p class="rx-eyebrow">Drug Safety Intelligence</p>
          <h1 class="rx-headline">
            Check before<br>it's dispensed.<br>
            <em>Every time.</em>
          </h1>
          <p class="rx-subline">
            Paste a prescription, upload a PDF, or photograph a label.
            The multi-agent pipeline checks interactions,
            contraindications, and suggests alternatives — locally, for free.
          </p>
          <div class="rx-features">
            <div class="rx-feat">
              <div class="rx-feat-icon">✓</div>
              <p class="rx-feat-text"><strong>Interaction detection</strong> — RxNorm · OpenFDA · LLM synthesis</p>
            </div>
            <div class="rx-feat">
              <div class="rx-feat-icon">✓</div>
              <p class="rx-feat-text"><strong>Contraindication check</strong> — patient profile aware</p>
            </div>
            <div class="rx-feat">
              <div class="rx-feat-icon">✓</div>
              <p class="rx-feat-text"><strong>Safer alternatives</strong> — same class, lower risk</p>
            </div>
            <div class="rx-feat">
              <div class="rx-feat-icon">✓</div>
              <p class="rx-feat-text"><strong>100 % local</strong> — Ollama, no data leaves your machine</p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # RIGHT: input in cream
    with col_right:
        # Wrap everything in the cream background div
        st.markdown('<div class="rx-right-bg">', unsafe_allow_html=True)
        st.markdown('<p class="rx-input-label">Enter prescription</p>', unsafe_allow_html=True)

        tab_t, tab_p, tab_i = st.tabs(["✏  Text", "  PDF", "◧  Image"])
        patient_info_val = {"age":None,"conditions":[],"allergies":[]}

        with tab_t:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            st.markdown('<p class="rx-ex-label">Quick examples</p>', unsafe_allow_html=True)

            ex1, ex2 = st.columns(2, gap="small")
            ex3, ex4 = st.columns(2, gap="small")
            examples = [
                ("Warfarin + Aspirin",  "Warfarin 5mg OD, Aspirin 81mg OD, Omeprazole 20mg OD"),
                ("Serotonin risk",      "Sertraline 50mg OD, Tramadol 50mg TID PRN"),
                ("Polypharmacy",        "Warfarin 5mg, Aspirin 81mg, Ibuprofen 400mg TID, Fluoxetine 20mg OD"),
                ("Safe combo",          "Amlodipine 5mg OD, Atorvastatin 40mg OD, Ramipril 5mg OD"),
            ]
            for col, (label, text) in zip([ex1, ex2, ex3, ex4], examples):
                with col:
                    if st.button(label, key=f"ex_{label}", use_container_width=True):
                        st.session_state.sample_text = text
                        st.rerun()

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            prescription_text = st.text_area("rx", value=st.session_state.sample_text, height=110,
                placeholder="e.g. Warfarin 5mg OD, Aspirin 81mg OD, Metformin 500mg BD")

            with st.expander("＋  Patient context  (age · conditions · allergies)"):
                a1, a2, a3 = st.columns([1,2,2], gap="small")
                with a1: p_age    = st.number_input("Age",min_value=0,max_value=120,value=0,step=1)
                with a2: p_cond   = st.text_area("Conditions",placeholder="Type 2 diabetes\nHypertension",height=76)
                with a3: p_allerg = st.text_area("Allergies",placeholder="Penicillin\nSulfa drugs",height=76)
                patient_info_val = {
                    "age":        int(p_age) if p_age else None,
                    "conditions": [c.strip() for c in p_cond.splitlines()  if c.strip()],
                    "allergies":  [a.strip() for a in p_allerg.splitlines() if a.strip()],
                }

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            if st.button("Analyse prescription  →", type="primary", use_container_width=True, key="btn_t"):
                if not prescription_text.strip():
                    st.warning("Please enter a prescription.")
                else:
                    with st.spinner("Running analysis…"):
                        try:
                            st.session_state.report = run_check(prescription_text,"text",patient_info_val)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Pipeline error: {e}")

        with tab_p:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            up_pdf = st.file_uploader("pdf", type=["pdf"])
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            if st.button("Analyse PDF  →", type="primary", use_container_width=True, key="btn_p"):
                if not up_pdf: st.warning("Please upload a PDF.")
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(up_pdf.read()); path = tmp.name
                    with st.spinner("Extracting and analysing…"):
                        try:
                            st.session_state.report = run_check(path,"pdf",patient_info_val)
                            os.unlink(path); st.rerun()
                        except Exception as e:
                            try: os.unlink(path)
                            except: pass
                            st.error(f"Error: {e}")

        with tab_i:
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            st.markdown("""<div style="background:#eff6ff;border:1px solid #dbeafe;border-radius:8px;
                padding:10px 14px;font-size:13px;color:#1e3a8a;margin-bottom:12px;line-height:1.6">
                <strong>Tip</strong> — Tesseract OCR first; then <code>llama3.2-vision</code> / <code>llava</code>.
                </div>""", unsafe_allow_html=True)
            up_img = st.file_uploader("img", type=["png","jpg","jpeg","tiff","bmp"])
            if up_img: st.image(up_img, width=220)
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            if st.button("Analyse image  →", type="primary", use_container_width=True, key="btn_i"):
                if not up_img: st.warning("Please upload an image.")
                else:
                    ext = os.path.splitext(up_img.name)[1] or ".png"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                        tmp.write(up_img.read()); path = tmp.name
                    with st.spinner("OCR → vision → analysis…"):
                        try:
                            st.session_state.report = run_check(path,"image",patient_info_val)
                            os.unlink(path); st.rerun()
                        except Exception as e:
                            try: os.unlink(path)
                            except: pass
                            st.error(f"Error: {e}")

        st.markdown("</div>", unsafe_allow_html=True)  # close rx-right-bg


# ═══════════════════════════════════════════════════════════════════════════════
# SCREEN B  —  Full-screen results: main content + right panel
# ═══════════════════════════════════════════════════════════════════════════════
def screen_results(r):
    # ── Nav with back button ──────────────────────────────────────────────────
    nav_l, nav_r = st.columns([1,1], gap="small")
    with nav_l:
        st.markdown("""
        <nav class="rx-nav" style="position:relative;z-index:999">
          <div class="rx-logo">
            <div class="rx-logo-icon">⚕</div>
            <span class="rx-logo-text">RxCheck</span>
          </div>
        </nav>
        """, unsafe_allow_html=True)
    with nav_r:
        st.markdown("""
        <div style="background:var(--white);border-bottom:1px solid var(--border);
                    border-left:1px solid var(--border);height:56px;
                    display:flex;align-items:center;padding:0 28px;
                    position:sticky;top:0;z-index:999">
        """, unsafe_allow_html=True)
        st.markdown('<div class="rx-back">', unsafe_allow_html=True)
        if st.button("← New check", key="back"):
            st.session_state.report = None
            st.session_state.sample_text = ""
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Error state
    err = r.get("error") if isinstance(r,dict) else None
    if err:
        st.markdown(f"""<div style="max-width:700px;margin:40px auto;padding:0 48px">
          <div style="background:#fff1f2;border:1px solid #fee2e2;border-radius:12px;
                      padding:16px 20px;color:#991b1b;font-size:14px">⚠ {err}</div>
        </div>""", unsafe_allow_html=True)
        return

    sev    = r.get("overall_severity","SAFE")
    urg    = r.get("urgency","ROUTINE")
    drugs  = r.get("drugs_analyzed",[])
    ixs    = r.get("interactions",[])
    cis    = r.get("contraindications",[])
    alts   = r.get("alternatives",[])
    web    = r.get("web_findings",[])
    summ   = r.get("clinical_summary","")
    recs   = r.get("key_recommendations",[])
    rep_id = r.get("report_id","")
    gen_at = r.get("generated_at","")[:19].replace("T"," ")
    disclm = r.get("disclaimer","")

    # ── Two-col layout: wide main + narrow side panel ─────────────────────────
    col_main, col_side = st.columns([1, 1], gap="small")

    # ── MAIN CONTENT ──────────────────────────────────────────────────────────
    with col_main:
        st.markdown('<div style="background:var(--white);min-height:calc(100vh - 56px);padding:44px 52px;border-right:1px solid var(--border)">', unsafe_allow_html=True)

        # Pipeline steps
        steps = ["Parsed","Interactions","Severity","Report"]
        nodes = "".join([
            f'<div class="rx-step">'
            f'<div class="rx-step-dot"><span class="rx-step-num">{i+1}</span></div>'
            f'<span class="rx-step-lbl">{lbl}</span>'
            + (f'<div class="rx-step-line"></div>' if i<3 else "")
            + f'</div>'
            for i,lbl in enumerate(steps)
        ])
        st.markdown(f'<div class="rx-steps">{nodes}</div>', unsafe_allow_html=True)

        # Alert banner
        has_issue = sev not in ("SAFE","LOW") or bool(cis)
        if has_issue:
            bc = {"MODERATE":("#fffbeb","#fde68a","#92400e","⚠"),
                  "HIGH":    ("#fff1f2","#fee2e2","#991b1b","⚠"),
                  "CRITICAL":("#fff1f2","#fee2e2","#991b1b","⚠")}
            bb,bl,bf,bi = bc.get(sev,("#fffbeb","#fde68a","#92400e","⚠"))
            parts = []
            if ixs: parts.append(f"{len(ixs)} interaction{'s' if len(ixs)>1 else ''}")
            if cis: parts.append(f"{len(cis)} contraindication{'s' if len(cis)>1 else ''}")
            st.markdown(f"""
            <div class="rx-banner" style="background:{bb};border:1px solid {bl}">
              <div style="display:flex;align-items:center;gap:14px">
                <span style="font-size:20px;color:{bf};flex-shrink:0">{bi}</span>
                <div>
                  <p style="font-size:14px;font-weight:600;color:{bf};margin-bottom:2px;font-family:Geist,sans-serif">{sev} severity detected</p>
                  <p style="font-size:13px;color:{bf};opacity:0.75;font-family:Geist,sans-serif">{" · ".join(parts)}</p>
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:8px;flex-shrink:0">{sev_pill(sev)}{urg_badge(urg)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="rx-banner" style="background:#f0fdf4;border:1px solid #dcfce7">
              <div style="display:flex;align-items:center;gap:14px">
                <span style="font-size:20px;color:#166534">✓</span>
                <p style="font-size:14px;font-weight:600;color:#166534;font-family:Geist,sans-serif">No significant interactions detected</p>
              </div>
              <div style="display:flex;align-items:center;gap:8px;flex-shrink:0">{sev_pill(sev)}{urg_badge(urg)}</div>
            </div>
            """, unsafe_allow_html=True)

        # Summary
        if summ:
            st.markdown(f"""<p class="rx-sec">Clinical Summary</p>
            <div class="rx-card" style="background:#eff6ff;border-color:#dbeafe;border-left:3px solid #1e3a8a;margin-bottom:20px">
              <p style="font-size:14px;color:#1e3a8a;line-height:1.75;font-family:Geist,sans-serif">{summ}</p>
            </div>""", unsafe_allow_html=True)

        # Recommendations
        if recs:
            items = "".join(f'<li style="margin-bottom:7px;font-size:14px;color:#166534;line-height:1.55;font-family:Geist,sans-serif">{rec}</li>' for rec in recs)
            st.markdown(f"""<p class="rx-sec">Key Recommendations</p>
            <div class="rx-card" style="background:#f0fdf4;border-color:#dcfce7;border-left:3px solid #16a34a;margin-bottom:20px">
              <ul style="margin:0;padding-left:18px">{items}</ul>
            </div>""", unsafe_allow_html=True)

        # Two-col: interactions + contraindications
        cx, cy = st.columns(2, gap="medium")
        with cx:
            st.markdown(f'<p class="rx-sec">Interactions ({len(ixs)})</p>', unsafe_allow_html=True)
            if ixs:
                for ix in ixs:
                    s = ix.get("severity","LOW")
                    st.markdown(f"""
                    <div class="rx-card" style="border-left:3px solid {lc(s)}">
                      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap">
                        {sev_pill(s)}
                        <span style="font-size:13px;font-weight:600;color:#18181a;font-family:Geist,sans-serif">
                          {ix.get('drug1','?').title()} ↔ {ix.get('drug2','?').title()}
                        </span>
                      </div>
                      <p style="font-size:13px;color:#52525b;line-height:1.55;margin-bottom:6px;font-family:Geist,sans-serif">{ix.get('description','')}</p>
                      <p style="font-size:12px;color:#a1a1aa;font-family:Geist,sans-serif">→ {ix.get('recommendation','')}</p>
                      <p style="font-size:11px;color:#d4d4d8;margin-top:4px;font-family:Geist,sans-serif">{ix.get('source','')}</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="rx-card" style="background:#f0fdf4;border-color:#dcfce7;font-size:14px;color:#166534;font-weight:500;font-family:Geist,sans-serif">✓ No interactions found</div>', unsafe_allow_html=True)

        with cy:
            st.markdown(f'<p class="rx-sec">Contraindications ({len(cis)})</p>', unsafe_allow_html=True)
            if cis:
                for ci in cis:
                    s = ci.get("severity","HIGH")
                    st.markdown(f"""
                    <div class="rx-card" style="border-left:3px solid {lc(s)}">
                      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;flex-wrap:wrap">
                        {sev_pill(s)}
                        <span style="font-size:13px;font-weight:600;color:#18181a;font-family:Geist,sans-serif">{ci.get('drug','?').title()}</span>
                      </div>
                      <p style="font-size:12px;font-weight:600;color:#52525b;margin-bottom:6px;font-family:Geist,sans-serif">{ci.get('condition','')}</p>
                      <p style="font-size:13px;color:#52525b;line-height:1.55;margin-bottom:6px;font-family:Geist,sans-serif">{ci.get('description','')}</p>
                      <p style="font-size:12px;color:#a1a1aa;font-family:Geist,sans-serif">→ {ci.get('recommendation','')}</p>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="rx-card" style="background:#f0fdf4;border-color:#dcfce7;font-size:14px;color:#166534;font-weight:500;font-family:Geist,sans-serif">✓ No contraindications found</div>', unsafe_allow_html=True)

        # Alternatives
        if alts:
            st.markdown(f'<p class="rx-sec" style="margin-top:20px">Alternatives ({len(alts)})</p>', unsafe_allow_html=True)
            n = min(len(alts),2)
            acols = st.columns(n, gap="medium")
            for col,alt in zip((acols*(len(alts)//n+1))[:len(alts)], alts):
                with col:
                    inner = "".join(
                        f'<div style="background:#f9fafb;border:1px solid #e4e4e7;border-radius:8px;padding:10px 14px;margin-top:8px">'
                        f'<p style="font-size:13px;font-weight:600;color:#166534;margin-bottom:3px;font-family:Geist,sans-serif">'
                        f'→ {a.get("name","").title()} <span style="font-weight:400;font-size:11px;color:#a1a1aa">· {a.get("class","")}</span></p>'
                        f'<p style="font-size:13px;color:#52525b;line-height:1.5;margin-bottom:4px;font-family:Geist,sans-serif">{a.get("rationale","")}</p>'
                        f'<p style="font-size:11px;color:#a1a1aa;font-family:Geist,sans-serif">{a.get("notes","")}</p></div>'
                        for a in alt.get("alternatives",[])
                    )
                    st.markdown(f'<div class="rx-card" style="border-left:3px solid #16a34a">'
                                f'<p style="font-size:14px;font-weight:600;color:#18181a;margin-bottom:3px;font-family:Geist,sans-serif">{alt.get("original_drug","").title()}</p>'
                                f'<p style="font-size:12px;color:#52525b;margin-bottom:4px;font-family:Geist,sans-serif">{alt.get("reason_for_change","")}</p>'
                                f'{inner}</div>', unsafe_allow_html=True)

        # Literature
        if web:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            with st.expander(f"Literature & adverse event findings  ({len(web)})"):
                for wf in web:
                    ds = ", ".join(wf.get("drugs_involved",[]))
                    st.markdown(f'<div style="padding:12px 4px;border-bottom:1px solid #e4e4e7">'
                                f'<p style="font-size:14px;font-weight:500;color:#18181a;margin-bottom:5px;font-family:Geist,sans-serif">{wf.get("finding","")}</p>'
                                f'<div style="display:flex;align-items:center;gap:10px;font-size:12px;color:#a1a1aa;font-family:Geist,sans-serif;flex-wrap:wrap">'
                                f'<span>{ds}</span><span>·</span>{sev_pill(wf.get("clinical_significance","LOW"))}'
                                f'<span>·</span><span>{wf.get("source","")}</span></div></div>',
                                unsafe_allow_html=True)

        # Disclaimer
        st.markdown(f'<div style="margin-top:32px;padding-top:20px;border-top:1px solid #e4e4e7">'
                    f'<p style="font-size:12px;color:#a1a1aa;line-height:1.6;font-family:Geist,sans-serif">⚕ {disclm}</p></div>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT PANEL ───────────────────────────────────────────────────────────
    with col_side:
        st.markdown('<div style="background:var(--cream);min-height:calc(100vh - 56px);padding:32px 36px">', unsafe_allow_html=True)

        # Report card
        sev_c = {"HIGH":"#991b1b","CRITICAL":"#991b1b","MODERATE":"#92400e"}.get(sev,"#166534")
        st.markdown(f"""
        <div class="rx-panel-card">
          <p class="rx-panel-title">Report</p>
          <p style="font-size:11px;color:#a1a1aa;font-family:Geist,sans-serif;margin-bottom:3px">{rep_id}</p>
          <p style="font-size:11px;color:#a1a1aa;font-family:Geist,sans-serif;margin-bottom:14px">{gen_at}</p>
          <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px">{sev_pill(sev)}{urg_badge(urg)}</div>
          <div style="line-height:2">{" ".join(drug_chip(d) for d in drugs)}</div>
        </div>
        """, unsafe_allow_html=True)

        # Stats grid
        st.markdown(f"""
        <div class="rx-panel-card">
          <p class="rx-panel-title">At a glance</p>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            <div style="background:var(--cream);border-radius:8px;padding:14px;text-align:center">
              <p style="font-size:10px;color:#a1a1aa;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:6px;font-family:Geist,sans-serif">Drugs</p>
              <p style="font-family:'Instrument Serif',serif;font-size:32px;color:#18181a;line-height:1">{len(drugs)}</p>
            </div>
            <div style="background:var(--cream);border-radius:8px;padding:14px;text-align:center">
              <p style="font-size:10px;color:#a1a1aa;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:6px;font-family:Geist,sans-serif">Interactions</p>
              <p style="font-family:'Instrument Serif',serif;font-size:32px;color:{sev_c};line-height:1">{len(ixs)}</p>
            </div>
            <div style="background:var(--cream);border-radius:8px;padding:14px;text-align:center">
              <p style="font-size:10px;color:#a1a1aa;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:6px;font-family:Geist,sans-serif">Contraind.</p>
              <p style="font-family:'Instrument Serif',serif;font-size:32px;color:{sev_c};line-height:1">{len(cis)}</p>
            </div>
            <div style="background:var(--cream);border-radius:8px;padding:14px;text-align:center">
              <p style="font-size:10px;color:#a1a1aa;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;margin-bottom:6px;font-family:Geist,sans-serif">Alternatives</p>
              <p style="font-family:'Instrument Serif',serif;font-size:32px;color:#18181a;line-height:1">{len(alts)}</p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Export
        st.markdown('<div class="rx-panel-card"><p class="rx-panel-title">Export</p>', unsafe_allow_html=True)
        st.download_button("↓ Download report (JSON)", data=json.dumps(r,indent=2),
                           file_name=f"rxcheck_{rep_id}.json", mime="application/json",
                           use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # close side panel


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.report:
    screen_results(st.session_state.report)
else:
    screen_landing()