"""
================================================================================
TALENTMATCH AI — Streamlit UI
================================================================================
Run:  streamlit run app.py
================================================================================
"""

import os
import json
import tempfile
import streamlit as st
from getpass import getpass

# ─────────────────────────────────────────────────────────────────────────────
# Page config — must be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TalentMatch AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — clean, professional dark-navy + teal palette
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0F172A 0%, #1E3A5F 100%);
    border-right: 1px solid #1E3A5F;
}
section[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] textarea {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #F8FAFC !important;
    border-radius: 8px;
}

/* ── Main area ─────────────────────────────────────────────────────────── */
.main .block-container {
    padding-top: 1.5rem;
    max-width: 1200px;
}

/* ── Hero header ───────────────────────────────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #0F172A 0%, #1B4D7A 60%, #0D9488 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(13,148,136,0.18);
}
.hero h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    color: #F0FDF4;
    margin: 0;
    letter-spacing: -1px;
}
.hero p {
    color: #A7F3D0;
    font-size: 1rem;
    margin: 0.4rem 0 0 0;
}

/* ── Score cards ───────────────────────────────────────────────────────── */
.score-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 0.6rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: transform 0.15s;
}
.score-card:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(0,0,0,0.1); }
.score-card.hire   { border-left: 5px solid #10B981; }
.score-card.maybe  { border-left: 5px solid #F59E0B; }
.score-card.nohire { border-left: 5px solid #EF4444; }

.score-badge {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #1B3A6B;
}
.rec-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.rec-HIRE    { background: #D1FAE5; color: #065F46; }
.rec-MAYBE   { background: #FEF3C7; color: #92400E; }
.rec-NOHIRE  { background: #FEE2E2; color: #991B1B; }

/* ── Dimension bars ────────────────────────────────────────────────────── */
.dim-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 6px 0;
    font-size: 0.85rem;
}
.dim-label { width: 160px; color: #475569; font-weight: 500; }
.dim-bar-bg {
    flex: 1;
    height: 10px;
    background: #F1F5F9;
    border-radius: 6px;
    overflow: hidden;
}
.dim-bar-fill {
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, #0D9488, #1B3A6B);
}
.dim-score { width: 40px; text-align: right; font-weight: 600; color: #1E293B; }

/* ── XAI section ───────────────────────────────────────────────────────── */
.xai-box {
    background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
    border: 1px solid #DDD6FE;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-top: 0.6rem;
}
.xai-title {
    font-family: 'Space Mono', monospace;
    color: #5B21B6;
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 8px;
}

/* ── Override form ─────────────────────────────────────────────────────── */
.override-box {
    background: #FFFBEB;
    border: 1px solid #FCD34D;
    border-radius: 10px;
    padding: 1rem;
}

/* ── Buttons ───────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #0D9488, #1B3A6B);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    font-family: 'DM Sans', sans-serif;
}
.stButton > button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

/* ── Progress bar ──────────────────────────────────────────────────────── */
.stProgress > div > div > div { background: linear-gradient(90deg, #0D9488, #1B3A6B); }

/* ── Metrics ───────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 0.8rem;
}

/* ── File uploader ─────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed #CBD5E1;
    border-radius: 10px;
    padding: 0.5rem;
}

div[data-baseweb="tab-list"] button {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Lazy import (so the app loads even without API key)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_agent_module():
    from src.agent import (
        init_llm, analyze_jd, read_resume, read_linkedin_json,
        extract_candidate, compute_tfidf_similarity, calculate_skill_match,
        score_candidate, explain_with_lime, explain_dimension_contributions,
        override_score, generate_pdf_report, run_agent, DELAY_BETWEEN_CANDIDATES
    )
    return dict(
        init_llm=init_llm, run_agent=run_agent,
        generate_pdf_report=generate_pdf_report,
        override_score=override_score,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Session state defaults
# ─────────────────────────────────────────────────────────────────────────────
for key, default in [
    ("results", []),
    ("jd_parsed", {}),
    ("llm", None),
    ("api_key_set", False),
    ("run_done", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Config
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎯 TalentMatch AI")
    st.markdown("---")

    st.markdown("### 🔑 API Configuration")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get your free key at aistudio.google.com",
    )
    if api_key and not st.session_state.api_key_set:
        try:
            with st.spinner("Connecting to Gemini…"):
                agents = get_agent_module()
                st.session_state.llm = agents["init_llm"](api_key)
                st.session_state.api_key_set = True
            st.success("✅ Connected!")
        except Exception as e:
            st.error(f"Connection failed: {e}")

    st.markdown("---")
    st.markdown("### 📋 Scoring Weights")
    st.caption("As per internship brief (read-only)")
    weights = {
        "Skills Match":      30,
        "Experience":        25,
        "Projects":          20,
        "Education & Certs": 15,
        "Communication":     10,
    }
    for dim, w in weights.items():
        st.markdown(
            f'<div class="dim-row"><span class="dim-label">{dim}</span>'
            f'<div class="dim-bar-bg"><div class="dim-bar-fill" style="width:{w*3}px"></div></div>'
            f'<span class="dim-score">{w}%</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### ℹ️ Stack")
    st.caption("LLM: Gemini 2.5 Flash\nFramework: LangChain LCEL\nXAI: LIME\nCache: SQLite\nReport: ReportLab")


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🎯 TalentMatch AI</h1>
  <p>AI-powered resume shortlisting · Explainable scoring · Human-in-the-loop · Audit trail</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_run, tab_results, tab_override, tab_audit = st.tabs([
    "📥  Run Agent", "📊  Results", "✏️  Override Scores", "🔍  Audit Log"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Run Agent
# ══════════════════════════════════════════════════════════════════════════════
with tab_run:
    col_jd, col_resumes = st.columns([1, 1], gap="large")

    with col_jd:
        st.markdown("### 📋 Job Description")
        jd_input_mode = st.radio("Input mode", ["Paste text", "Upload file"], horizontal=True)

        jd_text = ""
        if jd_input_mode == "Paste text":
            jd_text = st.text_area(
                "Paste JD here",
                height=320,
                placeholder="Senior Data Scientist\n\nRequired Skills: Python, TensorFlow…",
            )
        else:
            jd_file = st.file_uploader("Upload JD (TXT/PDF)", type=["txt", "pdf"])
            if jd_file:
                if jd_file.name.endswith(".pdf"):
                    import pypdf, io
                    reader = pypdf.PdfReader(io.BytesIO(jd_file.read()))
                    jd_text = "\n".join(p.extract_text() or "" for p in reader.pages)
                else:
                    jd_text = jd_file.read().decode("utf-8", errors="ignore")
                st.success(f"✅ Loaded: {jd_file.name}")

    with col_resumes:
        st.markdown("### 📄 Candidate Resumes")
        resume_files_uploaded = st.file_uploader(
            "Upload resumes (PDF / DOCX / TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )
        if resume_files_uploaded:
            st.success(f"✅ {len(resume_files_uploaded)} file(s) loaded")
            for f in resume_files_uploaded:
                st.caption(f"• {f.name}")

        st.markdown("#### LinkedIn JSON (optional)")
        linkedin_files_uploaded = st.file_uploader(
            "Upload exported LinkedIn JSON",
            type=["json"],
            accept_multiple_files=True,
        )

    st.markdown("---")

    # ── Load sample data ──────────────────────────────────────────────────────
    col_btn1, col_btn2, _ = st.columns([1, 1, 3])
    with col_btn1:
        use_sample = st.button("📝 Load Sample Data", use_container_width=True)
    with col_btn2:
        run_btn = st.button(
            "🚀 Run Agent",
            use_container_width=True,
            disabled=not st.session_state.api_key_set,
        )

    SAMPLE_JD = """
Senior Data Scientist

Required Skills: Python, Machine Learning, SQL, TensorFlow, scikit-learn, Docker, Git
Nice to have: NLP, MLflow, SHAP
Experience: 2–5 years in data science or ML roles
Education: B.Tech/M.Tech in Computer Science, Statistics, or related field
Domain: Fintech / E-commerce / SaaS
Certifications (preferred): AWS ML Specialty, Google ML Engineer

Responsibilities:
- Build and deploy production-grade ML models
- Communicate findings to non-technical stakeholders
- Drive projects end-to-end with clean, documented code
"""

    SAMPLE_RESUMES = {
        "jane_smith.txt": """
Jane Smith | jane@email.com | +91-98765-43210

SKILLS: Python, TensorFlow, PyTorch, scikit-learn, SQL, Docker, Git, AWS, MLflow, NLP

EXPERIENCE: Senior Data Scientist — FinTech Corp (2021–Present, 3.5 yrs)
- Credit risk XGBoost model, reduced defaults 18%
- NLP pipeline 95% accuracy, 10K daily users
- Led team of 3 junior data scientists

EDUCATION: M.Tech CS — IIT Delhi (2021) CGPA 9.1
CERTIFICATIONS: Google ML Engineer (2022), AWS ML Specialty (2023)

PROJECTS:
1. Loan Default Predictor — XGBoost + SHAP, 94% AUC, production
2. Real-time Fraud Detection — Kafka + ML, <50ms latency
3. NLP Sentiment Engine — BERT fine-tuned REST API
""",
        "arjun_mehta.txt": """
Arjun Mehta | arjun@gmail.com | Bangalore

SKILLS: Python, R, SQL, pandas, scikit-learn, Power BI, Statistics

EXPERIENCE: BI Analyst — RetailCo (2022–Present, 2.5 yrs)
- Sales forecasting reduced inventory waste 22%
- A/B testing for pricing strategy

EDUCATION: M.Sc Statistics — Delhi University (2021) 78%
CERTIFICATIONS: Coursera ML Specialization (2023)

PROJECTS:
Customer Churn Prediction — RandomForest, deployed Heroku
Stock Forecaster — LSTM model
""",
        "rahul_verma.txt": """
Rahul Verma | rahul@hotmail.com | Mumbai

SKILLS: Microsoft Excel, Financial Modelling, PowerPoint, SAP, Bloomberg Terminal

EXPERIENCE: Financial Analyst — BankCorp (2021–Present, 3 yrs)
- Monthly P&L reports
- Investment portfolio Excel models

EDUCATION: MBA Finance — Symbiosis (2021)

Note: Interested in switching to data science. No formal ML experience.
""",
    }

    if use_sample:
        st.session_state["sample_jd"] = SAMPLE_JD
        st.session_state["sample_resumes"] = SAMPLE_RESUMES
        st.info("✅ Sample data loaded — click **Run Agent** to evaluate.")

    # ── Run ────────────────────────────────────────────────────────────────────
    if run_btn:
        if not st.session_state.api_key_set:
            st.warning("Please enter your Gemini API key in the sidebar first.")
        else:
            agents = get_agent_module()

            # Resolve JD text
            active_jd = jd_text or st.session_state.get("sample_jd", "")
            if not active_jd.strip():
                st.error("Please provide a Job Description.")
                st.stop()

            # Resolve resume files
            tmp_dir = tempfile.mkdtemp()
            resume_paths = []

            if resume_files_uploaded:
                for uf in resume_files_uploaded:
                    path = os.path.join(tmp_dir, uf.name)
                    with open(path, "wb") as f:
                        f.write(uf.getvalue())
                    resume_paths.append(path)
            elif st.session_state.get("sample_resumes"):
                for fname, content in st.session_state["sample_resumes"].items():
                    path = os.path.join(tmp_dir, fname)
                    with open(path, "w") as f:
                        f.write(content)
                    resume_paths.append(path)

            if not resume_paths:
                st.error("Please upload at least one resume.")
                st.stop()

            linkedin_paths = []
            for lf in (linkedin_files_uploaded or []):
                path = os.path.join(tmp_dir, lf.name)
                with open(path, "wb") as f:
                    f.write(lf.getvalue())
                linkedin_paths.append(path)

            # Run with progress
            progress = st.progress(0, text="Starting agent…")
            status   = st.empty()

            steps = [
                (15, "📋 Parsing Job Description…"),
                (30, "📄 Loading resumes…"),
                (55, "🔍 Extracting profiles & computing similarity…"),
                (75, "📊 Scoring candidates (LLM rubric)…"),
                (90, "🔬 Generating XAI explanations…"),
                (98, "📝 Creating PDF report…"),
            ]

            import threading, time as _time

            def _run():
                results = agents["run_agent"](
                    jd_text=active_jd,
                    resume_files=resume_paths,
                    linkedin_files=linkedin_paths,
                    llm=st.session_state.llm,
                    generate_report=True,
                    report_path="outputs/shortlist_report.pdf",
                )
                st.session_state.results = results
                st.session_state.run_done = True

            thread = threading.Thread(target=_run)
            thread.start()

            for i, (pct, msg) in enumerate(steps):
                _time.sleep(1.5)
                progress.progress(pct, text=msg)

            thread.join()
            progress.progress(100, text="✅ Done!")
            _time.sleep(0.5)
            progress.empty()
            status.empty()

            if st.session_state.results:
                st.success(f"✅ Evaluated {len(st.session_state.results)} candidates. See **Results** tab.")
                # Offer PDF download
                if os.path.exists("outputs/shortlist_report.pdf"):
                    with open("outputs/shortlist_report.pdf", "rb") as f:
                        st.download_button(
                            "⬇️ Download PDF Report",
                            data=f,
                            file_name="talentmatch_report.pdf",
                            mime="application/pdf",
                        )
            else:
                st.error("Agent returned no results. Check API key and file formats.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Results
# ══════════════════════════════════════════════════════════════════════════════
with tab_results:
    if not st.session_state.results:
        st.info("Run the agent first (← Run Agent tab).")
    else:
        results = st.session_state.results

        # Summary metrics
        n_hire   = sum(1 for r in results if r["scores"]["recommendation"] == "HIRE")
        n_maybe  = sum(1 for r in results if r["scores"]["recommendation"] == "MAYBE")
        n_nohire = sum(1 for r in results if r["scores"]["recommendation"] == "NO HIRE")
        avg_score = sum(r["scores"]["total_score"] for r in results) / len(results)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Evaluated", len(results))
        c2.metric("✅ HIRE",    n_hire)
        c3.metric("🤔 MAYBE",   n_maybe)
        c4.metric("❌ NO HIRE", n_nohire)

        st.markdown("---")
        st.markdown("### Candidate Rankings")

        for r in results:
            name  = r["candidate_info"].get("name", "?")
            total = r["scores"]["total_score"]
            rec   = r["scores"]["recommendation"]
            rank  = r.get("rank", "?")
            sim   = r.get("embedding", {}).get("similarity_pct", "—")

            rec_class = {"HIRE": "hire", "MAYBE": "maybe"}.get(rec, "nohire")
            rec_badge_class = {"HIRE": "rec-HIRE", "MAYBE": "rec-MAYBE"}.get(rec, "rec-NOHIRE")

            with st.expander(f"#{rank}  {name}  —  {total}/10  ({rec})", expanded=(rank == 1)):
                col_score, col_info = st.columns([1, 2])

                with col_score:
                    st.markdown(
                        f'<div class="score-card {rec_class}">'
                        f'<div class="score-badge">{total}/10</div><br>'
                        f'<span class="rec-badge {rec_badge_class}">{rec}</span><br><br>'
                        f'<small>TF-IDF Similarity: <b>{sim}</b></small>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    # Skill match
                    sm = r["skill_match"]
                    st.caption(f"Skill Match: {sm['match_summary']}")
                    if sm["missing_skills"]:
                        st.caption(f"Missing: {', '.join(sm['missing_skills'][:4])}")

                with col_info:
                    st.markdown("**Dimension Scores**")
                    for d in r["scores"]["dimension_scores"]:
                        pct = int(d["score"] * 10)
                        st.markdown(
                            f'<div class="dim-row">'
                            f'<span class="dim-label">{d["dimension"]}</span>'
                            f'<div class="dim-bar-bg"><div class="dim-bar-fill" style="width:{pct}%"></div></div>'
                            f'<span class="dim-score">{d["score"]}/10</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        st.caption(f"↳ {d['justification']}")

                # XAI
                lime_feats = r.get("xai_features", [])
                contribs   = r.get("xai_contributions", [])
                if lime_feats or contribs:
                    st.markdown(
                        '<div class="xai-box"><div class="xai-title">🔬 XAI Insights</div>',
                        unsafe_allow_html=True,
                    )
                    if contribs:
                        c_str = "  |  ".join(
                            f"{c['dimension'].split()[0]}: {'+'if c['contribution']>=0 else ''}{c['contribution']:.3f}"
                            for c in contribs
                        )
                        st.caption(f"Dimension contributions vs baseline (5.0): {c_str}")
                    if lime_feats:
                        l_str = "  ".join(f"'{w}'({v:+.2f})" for w, v in lime_feats[:6])
                        st.caption(f"LIME keywords: {l_str}")
                    st.markdown('</div>', unsafe_allow_html=True)

                # Strengths / Concerns
                col_s, col_c = st.columns(2)
                with col_s:
                    st.markdown("**✨ Strengths**")
                    for s in r["scores"].get("strengths", []):
                        st.caption(f"• {s}")
                with col_c:
                    st.markdown("**⚠️ Concerns**")
                    for c in r["scores"].get("concerns", []):
                        st.caption(f"• {c}")

        # Download buttons
        st.markdown("---")
        col_dl1, col_dl2, _ = st.columns([1, 1, 3])
        with col_dl1:
            if os.path.exists("outputs/shortlist_report.pdf"):
                with open("outputs/shortlist_report.pdf", "rb") as f:
                    st.download_button("⬇️ PDF Report", f, "talentmatch_report.pdf", "application/pdf")
        with col_dl2:
            if os.path.exists("outputs/scored_candidates.json"):
                with open("outputs/scored_candidates.json") as f:
                    st.download_button("⬇️ JSON Data", f, "scored_candidates.json", "application/json")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Human Override
# ══════════════════════════════════════════════════════════════════════════════
with tab_override:
    st.markdown("### ✏️ Human-in-the-Loop Score Override")
    st.markdown(
        "Adjust any dimension score after AI evaluation. "
        "Every change is permanently logged to **audit_log.json**."
    )

    if not st.session_state.results:
        st.info("Run the agent first to enable overrides.")
    else:
        with st.container():
            st.markdown('<div class="override-box">', unsafe_allow_html=True)

            names = [r["candidate_info"]["name"] for r in st.session_state.results]
            c_name = st.selectbox("Select Candidate", names)
            dimension = st.selectbox(
                "Dimension to Override",
                ["Skills Match", "Experience", "Education & Certs", "Projects", "Communication"],
            )
            new_score = st.slider("New Score", 0.0, 10.0, 5.0, 0.5)
            reason    = st.text_input("Reason for override", placeholder="e.g. Strong GitHub portfolio shown at interview")
            reviewer  = st.text_input("Reviewer name", value="HR Manager")

            if st.button("Apply Override"):
                if not reason.strip():
                    st.warning("Please provide a reason.")
                else:
                    agents = get_agent_module()
                    st.session_state.results = agents["override_score"](
                        st.session_state.results,
                        candidate_name=c_name,
                        dimension=dimension,
                        new_score=new_score,
                        reason=reason,
                        reviewer=reviewer,
                    )
                    st.success(f"✅ Score updated for {c_name} — {dimension}: {new_score}/10")
                    # Regenerate PDF
                    if st.session_state.results:
                        agents["generate_pdf_report"](
                            st.session_state.results,
                            st.session_state.get("jd_parsed", {}),
                        )
                        st.caption("PDF report regenerated with override applied.")

            st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Audit Log
# ══════════════════════════════════════════════════════════════════════════════
with tab_audit:
    st.markdown("### 🔍 Audit Trail")
    st.caption("Every agent action is logged here. This log is also written to audit_log.json on disk.")

    log_path = "audit_log.json"
    if os.path.exists(log_path):
        entries = []
        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
        if entries:
            import pandas as pd
            df = pd.DataFrame(entries)
            st.dataframe(df, use_container_width=True, height=400)
            st.download_button("⬇️ Download Audit Log", open(log_path).read(),
                               "audit_log.json", "application/json")
        else:
            st.info("Audit log is empty.")
    else:
        st.info("No audit log yet. Run the agent to generate one.")
