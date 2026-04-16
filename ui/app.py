import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import json
import tempfile

st.set_page_config(
    page_title="RxCheck",
    page_icon="⚕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600&display=swap');

:root {
  --cream:#f7f5f0;--white:#ffffff;--ink:#18181a;--ink2:#52525b;--ink3:#a1a1aa;
  --border:#e4e4e7;--border2:#d4d4d8;
  --content-w:1120px;--report-w:860px;
  --green:#166534;--green-m:#16a34a;--green-l:#dcfce7;--green-b:#f0fdf4;
  --red:#991b1b;--red-m:#dc2626;--red-l:#fee2e2;--red-b:#fff1f2;
  --amber:#92400e;--amber-m:#d97706;--amber-l:#fde68a;--amber-b:#fffbeb;
  --blue:#1e3a8a;--blue-m:#2563eb;--blue-l:#dbeafe;--blue-b:#eff6ff;
  --shadow-s:0 1px 2px rgba(0,0,0,0.05);
  --shadow-m:0 4px 6px -1px rgba(0,0,0,0.07),0 2px 4px -1px rgba(0,0,0,0.04);
  --shadow-l:0 10px 15px -3px rgba(0,0,0,0.08),0 4px 6px -2px rgba(0,0,0,0.03);
  --r:12px;--r-sm:8px;--r-xs:6px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{font-family:'Geist',sans-serif;}
.stApp{background:var(--cream);}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:0!important;max-width:100%!important;}
section[data-testid="stSidebar"]{display:none!important;}
[data-testid="collapsedControl"]{display:none!important;}

.stTabs [data-baseweb="tab-list"]{gap:2px;background:#f4f4f5;border:1px solid var(--border);border-radius:var(--r-sm);padding:3px;width:fit-content;margin:0 0 14px 0;}
.stTabs [data-baseweb="tab"]{border-radius:var(--r-xs);padding:7px 18px;font-size:13px;font-weight:500;color:var(--ink2);background:transparent;border:none;font-family:'Geist',sans-serif;height:34px;display:flex;align-items:center;justify-content:center;}
.stTabs [aria-selected="true"]{background:var(--white)!important;color:var(--ink)!important;font-weight:600!important;box-shadow:var(--shadow-s)!important;}
.stTabs [data-baseweb="tab-panel"]{padding-top:0!important;}

.stTextArea textarea{border-radius:var(--r-sm);border:1.5px solid var(--border);background:var(--white);color:var(--ink);font-size:15px;line-height:1.7;font-family:'Geist',sans-serif;padding:14px 16px;transition:border-color 0.15s,box-shadow 0.15s;box-shadow:var(--shadow-s);}
.stTextArea textarea:focus{border-color:var(--green-m)!important;box-shadow:0 0 0 3px rgba(22,163,74,0.12)!important;}
.stTextArea textarea::placeholder{color:var(--ink3);}
.stTextArea label{display:none!important;}
.stFileUploader label{display:none!important;}
.stFileUploader section{background:var(--white);border:1.5px dashed var(--border2);border-radius:var(--r);box-shadow:var(--shadow-s);}
.stFileUploader section:hover{border-color:var(--green-m);}

.stButton>button[kind="primary"]{background:var(--ink)!important;color:#fff!important;border:none!important;border-radius:var(--r-sm)!important;font-weight:600!important;font-size:15px!important;letter-spacing:-0.01em!important;padding:13px 0!important;font-family:'Geist',sans-serif!important;box-shadow:var(--shadow-m)!important;transition:all 0.15s!important;}
.stButton>button[kind="primary"]:hover{background:#27272a!important;box-shadow:var(--shadow-l)!important;transform:translateY(-1px)!important;}
.stButton>button:not([kind="primary"]){background:var(--white)!important;color:var(--ink2)!important;border:1px solid var(--border)!important;border-radius:var(--r-xs)!important;font-size:13px!important;font-weight:500!important;padding:6px 14px!important;font-family:'Geist',sans-serif!important;transition:all 0.12s!important;box-shadow:var(--shadow-s)!important;min-height:40px;}
.stButton>button:not([kind="primary"]):hover{border-color:var(--border2)!important;color:var(--ink)!important;background:#fafafa!important;}

.stDownloadButton>button{background:var(--white)!important;color:var(--ink2)!important;border:1px solid var(--border)!important;border-radius:var(--r-xs)!important;font-size:13px!important;font-weight:500!important;font-family:'Geist',sans-serif!important;box-shadow:var(--shadow-s)!important;transition:all 0.12s!important;}
.stDownloadButton>button:hover{color:var(--ink)!important;border-color:var(--border2)!important;}

.stNumberInput input{border-radius:var(--r-sm);border:1.5px solid var(--border);background:var(--white);font-family:'Geist',sans-serif;font-size:14px;transition:border-color 0.15s;}
.stNumberInput input:focus{border-color:var(--green-m)!important;box-shadow:0 0 0 3px rgba(22,163,74,0.12)!important;}
.stSpinner>div{border-top-color:var(--ink)!important;}
[data-testid="stExpander"]{background:var(--white)!important;border:1px solid var(--border)!important;border-radius:var(--r)!important;box-shadow:var(--shadow-s)!important;}
.stImage img{border-radius:var(--r);box-shadow:var(--shadow-m);}

[data-testid="column"] .stButton>button{white-space:nowrap;}
[data-testid="stHorizontalBlock"]{align-items:stretch;}

@media (max-width: 900px){
  [data-testid="stHorizontalBlock"]{gap:8px!important;}
}

@media (max-width: 768px){
  .stTabs [data-baseweb="tab"]{padding:6px 12px;font-size:12px;}
}
</style>
""", unsafe_allow_html=True)


def sev_pill(s):
    s=(s or "SAFE").upper()
    cfg={"SAFE":("var(--green-l)","var(--green)"),"LOW":("var(--amber-l)","var(--amber)"),
         "MODERATE":("var(--amber-b)","var(--amber)"),"HIGH":("var(--red-l)","var(--red)"),
         "CRITICAL":("var(--red-l)","var(--red)"),"CONTRAINDICATED":("var(--red-l)","var(--red)")}
    bg,fg=cfg.get(s,("var(--border)","var(--ink2)"))
    return f'<span style="display:inline-flex;align-items:center;gap:4px;background:{bg};color:{fg};padding:3px 10px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:0.06em;font-family:Geist,sans-serif">● {s}</span>'

def urg_badge(u):
    u=(u or "ROUTINE").upper()
    cfg={"EMERGENCY":("var(--red-l)","var(--red)","⚠"),"URGENT":("var(--amber-l)","var(--amber)","!"),"ROUTINE":("var(--green-l)","var(--green)","✓")}
    bg,fg,icon=cfg.get(u,("var(--border)","var(--ink2)","·"))
    return f'<span style="display:inline-flex;align-items:center;gap:5px;background:{bg};color:{fg};padding:4px 12px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:0.06em;font-family:Geist,sans-serif">{icon} {u}</span>'

def drug_chip(name):
    return (f'<span style="display:inline-flex;align-items:center;gap:5px;background:var(--white);'
            f'color:var(--ink2);border:1px solid var(--border);padding:4px 12px;border-radius:999px;'
            f'font-size:12px;font-weight:500;font-family:Geist,sans-serif;margin:2px">'
            f'<span style="width:6px;height:6px;border-radius:50%;background:var(--ink3);'
            f'display:inline-block"></span>{name.title()}</span>')

def run_check(raw_input, input_type, patient_info):
    state={"raw_input":raw_input,"input_type":input_type,"drugs":[],"patient_info":patient_info,
           "interactions":[],"contraindications":[],"web_findings":[],"severity_score":"SAFE",
           "alternatives":[],"report":{},"error":None,"next":"ingestion",
           "parallel_checks_complete":False,"alternatives_complete":False}
    result=st.session_state.graph.invoke(state)
    return result.get("report",{})


if "graph" not in st.session_state:
    with st.spinner("Warming up pipeline…"):
        from graph.builder import build_graph
        st.session_state.graph=build_graph()
if "report" not in st.session_state: st.session_state.report=None
if "sample_text" not in st.session_state: st.session_state.sample_text=""


# ── NAV ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:var(--white);border-bottom:1px solid var(--border);padding:0 40px;
            display:flex;align-items:center;justify-content:space-between;height:56px">
  <div style="width:100%;max-width:var(--content-w);margin:0 auto;display:flex;align-items:center;justify-content:space-between">
  <div style="display:flex;align-items:center;gap:10px">
    <div style="width:28px;height:28px;background:var(--ink);border-radius:7px;
                display:flex;align-items:center;justify-content:center">
      <span style="color:white;font-size:14px">⚕</span>
    </div>
    <span style="font-family:'Instrument Serif',serif;font-size:20px;color:var(--ink);
                 letter-spacing:-0.02em">RxCheck</span>
  </div>
  <span style="font-size:12px;color:var(--ink3)">Free · local · open source · LangGraph + Ollama</span>
</div>
</div>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:var(--white);border-bottom:1px solid var(--border);padding:44px 40px 36px">
  <div style="max-width:var(--content-w);margin:0 auto">
  <div style="max-width:780px">
    <p style="font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;
              color:var(--ink3);margin-bottom:10px">Drug Safety Check</p>
    <h1 style="font-family:'Instrument Serif',serif;font-size:42px;font-weight:400;
               color:var(--ink);letter-spacing:-0.03em;line-height:1.1;margin-bottom:12px">
      Check your prescription<br>
      <em style="color:var(--ink2)">before it's dispensed</em>
    </h1>
    <p style="font-size:15px;color:var(--ink2);line-height:1.65;max-width:540px">
      Paste a prescription, upload a PDF, or photograph a label — 
      the multi-agent pipeline checks interactions, contraindications, 
      and suggests safer alternatives.
    </p>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

# ── INPUT ZONE ────────────────────────────────────────────────────────────────
st.markdown('<div style="max-width:var(--report-w);margin:0 auto;padding:28px 40px 0">', unsafe_allow_html=True)

tab_t, tab_p, tab_i = st.tabs(["✏ Text input", "📄 PDF upload", "🖼 Image / photo"])
patient_info_val = {"age":None,"conditions":[],"allergies":[]}

with tab_t:
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Example buttons
    st.markdown('<p style="font-size:12px;color:var(--ink3);margin-bottom:8px;font-weight:500;letter-spacing:0.02em">Quick examples</p>', unsafe_allow_html=True)
    ex1,ex2,ex3,ex4=st.columns(4)
    examples=[("Warfarin + Aspirin","Warfarin 5mg OD, Aspirin 81mg OD, Omeprazole 20mg OD"),
              ("Serotonin risk","Sertraline 50mg OD, Tramadol 50mg TID PRN"),
              ("Polypharmacy","Warfarin 5mg, Aspirin 81mg, Ibuprofen 400mg TID, Fluoxetine 20mg OD"),
              ("Safe combo","Amlodipine 5mg OD, Atorvastatin 40mg OD, Ramipril 5mg OD")]
    for col,(label,text) in zip([ex1,ex2,ex3,ex4],examples):
        with col:
            if st.button(label,key=f"ex_{label}",use_container_width=True):
                st.session_state.sample_text=text
                st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    prescription_text=st.text_area("prescription",value=st.session_state.sample_text,height=120,
        placeholder="e.g.  Warfarin 5mg once daily,  Aspirin 81mg OD,  Metformin 500mg BD")

    with st.expander("+ Add patient context  (age, conditions, allergies)", expanded=False):
        pc1,pc2,pc3=st.columns([1,2,2])
        with pc1: p_age=st.number_input("Age",min_value=0,max_value=120,value=0,step=1)
        with pc2: p_cond=st.text_area("Conditions",placeholder="Type 2 diabetes\nHypertension",height=80)
        with pc3: p_allerg=st.text_area("Allergies",placeholder="Penicillin\nSulfa drugs",height=80)
        patient_info_val={"age":int(p_age) if p_age else None,
                          "conditions":[c.strip() for c in p_cond.splitlines() if c.strip()],
                          "allergies":[a.strip() for a in p_allerg.splitlines() if a.strip()]}

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if st.button("Analyse prescription  →",type="primary",use_container_width=True,key="btn_t"):
        if not prescription_text.strip(): st.warning("Please enter a prescription.")
        else:
            with st.spinner("Running analysis…"):
                try: st.session_state.report=run_check(prescription_text,"text",patient_info_val)
                except Exception as e: st.error(f"Pipeline error: {e}")

with tab_p:
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    up_pdf=st.file_uploader("pdf",type=["pdf"])
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("Analyse PDF  →",type="primary",use_container_width=True,key="btn_p"):
        if not up_pdf: st.warning("Please upload a PDF.")
        else:
            with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
                tmp.write(up_pdf.read()); path=tmp.name
            with st.spinner("Extracting and analysing…"):
                try:
                    st.session_state.report=run_check(path,"pdf",patient_info_val)
                    os.unlink(path)
                except Exception as e:
                    try: os.unlink(path)
                    except: pass
                    st.error(f"Pipeline error: {e}")

with tab_i:
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="background:var(--blue-b);border:1px solid var(--blue-l);
        border-radius:var(--r-sm);padding:10px 14px;margin-bottom:12px;font-size:13px;color:var(--blue)">
      <strong>Tip</strong> — use a sharp, well-lit photo. Tesseract OCR runs first; if it finds &lt;20
      characters a vision model (<code>llama3.2-vision</code> or <code>llava</code>) is tried automatically.
    </div>""", unsafe_allow_html=True)
    up_img=st.file_uploader("image",type=["png","jpg","jpeg","tiff","bmp"])
    if up_img: st.image(up_img,width=260)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    if st.button("Analyse image  →",type="primary",use_container_width=True,key="btn_i"):
        if not up_img: st.warning("Please upload an image.")
        else:
            ext=os.path.splitext(up_img.name)[1] or ".png"
            with tempfile.NamedTemporaryFile(delete=False,suffix=ext) as tmp:
                tmp.write(up_img.read()); path=tmp.name
            with st.spinner("OCR → vision model → analysis…"):
                try:
                    st.session_state.report=run_check(path,"image",patient_info_val)
                    os.unlink(path)
                except Exception as e:
                    try: os.unlink(path)
                    except: pass
                    st.error(f"Pipeline error: {e}")

st.markdown('</div>', unsafe_allow_html=True)


# ── REPORT ────────────────────────────────────────────────────────────────────
if st.session_state.report:
    r=st.session_state.report
    err=r.get("error") if isinstance(r,dict) else None
    if err:
        st.markdown(f'<div style="max-width:820px;margin:24px auto;padding:0 40px">'
                    f'<div style="background:var(--red-b);border:1px solid var(--red-l);'
                    f'border-radius:var(--r);padding:16px 20px;color:var(--red);font-size:14px">⚠ {err}</div>'
                    f'</div>', unsafe_allow_html=True)
    else:
        sev=r.get("overall_severity","SAFE"); urg=r.get("urgency","ROUTINE")
        drugs=r.get("drugs_analyzed",[]); ixs=r.get("interactions",[])
        cis=r.get("contraindications",[]); alts=r.get("alternatives",[])
        web=r.get("web_findings",[]); summ=r.get("clinical_summary","")
        recs=r.get("key_recommendations",[]); rep_id=r.get("report_id","")
        gen_at=r.get("generated_at","")[:19].replace("T"," ")
        disclm=r.get("disclaimer","")

        # ── Pipeline steps ────────────────────────────────────────────────────
        steps=["Prescription parsed","Interactions checked","Severity scored","Report ready"]
        steps_html="".join([
            f'<div style="display:flex;align-items:center;flex:1">'
            f'<div style="display:flex;align-items:center;gap:8px">'
            f'<div style="width:22px;height:22px;border-radius:50%;background:var(--ink);'
            f'display:flex;align-items:center;justify-content:center;flex-shrink:0">'
            f'<span style="color:white;font-size:10px;font-weight:700">{i+1}</span></div>'
            f'<span style="font-size:12px;font-weight:600;color:var(--ink)">{lbl}</span></div>'
            f'{"<div style=flex:1;height:1px;background:var(--border);margin:0 12px></div>" if i<3 else ""}'
            f'</div>'
            for i,lbl in enumerate(steps)
        ])
        st.markdown(f"""
        <div style="background:var(--white);border-top:1px solid var(--border);
                    border-bottom:1px solid var(--border);padding:18px 40px">
          <div style="max-width:var(--report-w);margin:0 auto">
            <p style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                      color:var(--ink3);margin-bottom:12px">Analysis pipeline — complete</p>
            <div style="display:flex;align-items:center">{steps_html}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="max-width:var(--report-w);margin:0 auto;padding:28px 40px">', unsafe_allow_html=True)

        # ── Alert banner ──────────────────────────────────────────────────────
        has_issue=sev not in ("SAFE","LOW") or cis
        if has_issue:
            sev_cfg={"MODERATE":("var(--amber-b)","var(--amber-l)","var(--amber)","⚠"),
                     "HIGH":("var(--red-b)","var(--red-l)","var(--red)","⚠"),
                     "CRITICAL":("var(--red-b)","var(--red-l)","var(--red)","⚠")}
            bb,bl,bf,bi=sev_cfg.get(sev,("var(--amber-b)","var(--amber-l)","var(--amber)","⚠"))
            parts=[]
            if ixs: parts.append(f"{len(ixs)} interaction{'s' if len(ixs)>1 else ''}")
            if cis: parts.append(f"{len(cis)} contraindication{'s' if len(cis)>1 else ''}")
            st.markdown(f"""
            <div style="background:{bb};border:1px solid {bl};border-radius:var(--r);
                        padding:16px 20px;margin-bottom:20px;
                        display:flex;align-items:center;justify-content:space-between">
              <div style="display:flex;align-items:center;gap:14px">
                <span style="font-size:20px;color:{bf}">{bi}</span>
                <div>
                  <p style="font-size:14px;font-weight:600;color:{bf};margin-bottom:2px">{sev} severity detected</p>
                  <p style="font-size:13px;color:{bf};opacity:0.75">{" · ".join(parts)}</p>
                </div>
              </div>
              <div style="display:flex;align-items:center;gap:8px">{sev_pill(sev)}{urg_badge(urg)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:var(--green-b);border:1px solid var(--green-l);border-radius:var(--r);
                        padding:16px 20px;margin-bottom:20px;
                        display:flex;align-items:center;justify-content:space-between">
              <div style="display:flex;align-items:center;gap:14px">
                <span style="font-size:20px;color:var(--green)">✓</span>
                <p style="font-size:14px;font-weight:600;color:var(--green)">No significant interactions detected</p>
              </div>
              <div style="display:flex;align-items:center;gap:8px">{sev_pill(sev)}{urg_badge(urg)}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Meta + chips + download ───────────────────────────────────────────
        cl,cr=st.columns([3,1])
        with cl:
            chips_html=" ".join(drug_chip(d) for d in drugs)
            st.markdown(f'<p style="font-size:11px;color:var(--ink3);margin-bottom:8px">{rep_id} · {gen_at}</p>'
                        f'<div style="margin-bottom:18px">{chips_html}</div>',unsafe_allow_html=True)
        with cr:
            st.download_button("↓ Export JSON",data=json.dumps(r,indent=2),
                               file_name=f"rxcheck_{rep_id}.json",mime="application/json",
                               use_container_width=True)

        # ── Summary ───────────────────────────────────────────────────────────
        if summ:
            st.markdown(f"""
            <div style="background:var(--blue-b);border:1px solid var(--blue-l);border-radius:var(--r);
                        padding:18px 22px;margin-bottom:16px">
              <p style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                        color:var(--blue);margin-bottom:8px">Clinical Summary</p>
              <p style="font-size:14px;color:var(--blue);line-height:1.7">{summ}</p>
            </div>
            """, unsafe_allow_html=True)

        # ── Recommendations ───────────────────────────────────────────────────
        if recs:
            items="".join(f'<li style="margin-bottom:7px;font-size:14px;color:var(--green);line-height:1.55">{rec}</li>' for rec in recs)
            st.markdown(f"""
            <div style="background:var(--green-b);border:1px solid var(--green-l);border-radius:var(--r);
                        padding:18px 22px;margin-bottom:16px">
              <p style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
                        color:var(--green);margin-bottom:10px">Key Recommendations</p>
              <ul style="margin:0;padding-left:18px">{items}</ul>
            </div>
            """, unsafe_allow_html=True)

        # ── Two-column: interactions + contraindications ───────────────────────
        col_ix,col_ci=st.columns(2,gap="medium")

        def left_color(s):
            return {"HIGH":"var(--red-m)","CRITICAL":"var(--red-m)",
                    "CONTRAINDICATED":"var(--red-m)","MODERATE":"var(--amber-m)"}.get(s.upper(),"var(--border2)")

        with col_ix:
            st.markdown(f'<p style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink3);margin-bottom:10px">Drug Interactions ({len(ixs)})</p>',unsafe_allow_html=True)
            if ixs:
                for ix in ixs:
                    s=ix.get("severity","LOW")
                    st.markdown(f"""
                    <div style="background:var(--white);border:1px solid var(--border);border-left:3px solid {left_color(s)};
                                border-radius:var(--r);padding:14px 16px;margin-bottom:10px;box-shadow:var(--shadow-s)">
                      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                        {sev_pill(s)}
                        <span style="font-size:13px;font-weight:600;color:var(--ink)">
                          {ix.get('drug1','?').title()} ↔ {ix.get('drug2','?').title()}
                        </span>
                      </div>
                      <p style="font-size:13px;color:var(--ink2);line-height:1.55;margin-bottom:6px">{ix.get('description','')}</p>
                      <p style="font-size:12px;color:var(--ink3)">→ {ix.get('recommendation','')}</p>
                      <p style="font-size:11px;color:var(--border2);margin-top:4px">{ix.get('source','')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="background:var(--green-b);border:1px solid var(--green-l);border-radius:var(--r);padding:14px 16px;font-size:14px;color:var(--green);font-weight:500">✓ No interactions found</div>',unsafe_allow_html=True)

        with col_ci:
            st.markdown(f'<p style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink3);margin-bottom:10px">Contraindications ({len(cis)})</p>',unsafe_allow_html=True)
            if cis:
                for ci in cis:
                    s=ci.get("severity","HIGH")
                    st.markdown(f"""
                    <div style="background:var(--white);border:1px solid var(--border);border-left:3px solid {left_color(s)};
                                border-radius:var(--r);padding:14px 16px;margin-bottom:10px;box-shadow:var(--shadow-s)">
                      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">
                        {sev_pill(s)}
                        <span style="font-size:13px;font-weight:600;color:var(--ink)">{ci.get('drug','?').title()}</span>
                      </div>
                      <p style="font-size:12px;font-weight:500;color:var(--ink2);margin-bottom:6px">{ci.get('condition','')}</p>
                      <p style="font-size:13px;color:var(--ink2);line-height:1.55;margin-bottom:6px">{ci.get('description','')}</p>
                      <p style="font-size:12px;color:var(--ink3)">→ {ci.get('recommendation','')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="background:var(--green-b);border:1px solid var(--green-l);border-radius:var(--r);padding:14px 16px;font-size:14px;color:var(--green);font-weight:500">✓ No contraindications found</div>',unsafe_allow_html=True)

        # ── Alternatives ──────────────────────────────────────────────────────
        if alts:
            st.markdown(f'<p style="font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--ink3);margin:20px 0 10px">Suggested Alternatives ({len(alts)})</p>',unsafe_allow_html=True)
            n=min(len(alts),2)
            alt_cols=st.columns(n,gap="medium")
            for col,alt in zip(alt_cols*(len(alts)//n+1),alts):
                with col:
                    inner=""
                    for a in alt.get("alternatives",[]):
                        inner+=f'<div style="background:#f9fafb;border:1px solid var(--border);border-radius:var(--r-sm);padding:10px 14px;margin-top:8px"><p style="font-size:13px;font-weight:600;color:var(--green);margin-bottom:3px">→ {a.get("name","").title()} <span style="font-weight:400;font-size:11px;color:var(--ink3)">· {a.get("class","")}</span></p><p style="font-size:13px;color:var(--ink2);line-height:1.5;margin-bottom:4px">{a.get("rationale","")}</p><p style="font-size:11px;color:var(--ink3)">{a.get("notes","")}</p></div>'
                    st.markdown(f'<div style="background:var(--white);border:1px solid var(--border);border-left:3px solid var(--green-m);border-radius:var(--r);padding:16px 18px;box-shadow:var(--shadow-s)"><p style="font-size:14px;font-weight:600;color:var(--ink);margin-bottom:3px">{alt.get("original_drug","").title()}</p><p style="font-size:12px;color:var(--ink2);margin-bottom:4px">{alt.get("reason_for_change","")}</p>{inner}</div>',unsafe_allow_html=True)

        # ── Literature ────────────────────────────────────────────────────────
        if web:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            with st.expander(f"Literature & adverse event findings  ({len(web)})", expanded=False):
                for wf in web:
                    sig=wf.get("clinical_significance","LOW")
                    ds=", ".join(wf.get("drugs_involved",[]))
                    st.markdown(f'<div style="padding:12px 4px;border-bottom:1px solid var(--border)"><p style="font-size:14px;font-weight:500;color:var(--ink);margin-bottom:5px">{wf.get("finding","")}</p><div style="display:flex;align-items:center;gap:10px;font-size:12px;color:var(--ink3)"><span>{ds}</span><span>·</span>{sev_pill(sig)}<span>·</span><span>{wf.get("source","")}</span></div></div>',unsafe_allow_html=True)

        # ── Disclaimer ────────────────────────────────────────────────────────
        st.markdown(f'<div style="margin-top:32px;padding-top:20px;border-top:1px solid var(--border)"><p style="font-size:12px;color:var(--ink3);line-height:1.6">⚕ {disclm}</p></div>',unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid var(--border);background:var(--white);padding:16px 40px;margin-top:48px">
  <div style="max-width:var(--report-w);margin:0 auto;display:flex;align-items:center;justify-content:space-between">
    <span style="font-family:'Instrument Serif',serif;font-size:16px;color:var(--ink)">RxCheck</span>
    <span style="font-size:12px;color:var(--ink3)">Free · local · open source · not medical advice</span>
  </div>
</div>
""", unsafe_allow_html=True)