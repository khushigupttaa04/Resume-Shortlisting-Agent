"""
Run:  streamlit run app.py
"""

import os
import json
import tempfile
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
load_dotenv()
# ─────────────────────────────────────────────────────────────────────────────
# Page config — must be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Resume Shortlisting",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — warm beige/cream + MUSTARD YELLOW palette
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── PALETTE TOKENS ──────────────────────────────────────────────────────────
   Primary accent : #FFF9C4  (pastel yellow)
   Hover accent   : #FFF59D (pastel goldenrod)
   Background     : #F5F1EA  (warm cream)
   Sidebar bg     : #EDE8DF
   Text primary   : #1A1207  (near-black, warm)
   Text secondary : #4A3F2F  (dark brown)
─────────────────────────────────────────────────────────────────────────────*/

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #1A1207;
}

.stApp {
    background-color: #F5F1EA;
}

[data-testid="stAppViewContainer"] {
    background: #F5F1EA;
}

[data-testid="stHeader"] {
    background: #F5F1EA;
    border-bottom: none;
}

/* ─────────────────────────────────────────────────────────────
   SIDEBAR  — dark text throughout
───────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: #EDE8DF;
    border-right: 1px solid #D5CCBC;
    padding-top: 0.5rem;
}

/* Force every text node in sidebar to dark brown */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: #1A1207 !important;
}

section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] .stSelectbox div {
    background: white !important;
    border: 1px solid #C9B99A !important;
    color: #1A1207 !important;
    border-radius: 10px;
}

/* Sidebar info chips */
.sidebar-chip {
    display: inline-block;
    background: #D4A017;
    color: #1A1207 !important;
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 2px 0;
}

/* ─────────────────────────────────────────────────────────────
   MAIN AREA
───────────────────────────────────────────────────────────── */
.main .block-container {
    padding-top: 0rem;
    max-width: 1320px;
    padding-bottom: 2rem;
    background: #F5F1EA;
}

/* ─────────────────────────────────────────────────────────────
   HERO  — mustard yellow
───────────────────────────────────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #D4A017 0%, #E8C86A 100%);
    border-radius: 26px;
    padding: 2.8rem 3rem;
    margin-top: 0rem;
    margin-bottom: 2rem;
    box-shadow: 0 6px 32px rgba(212,160,23,0.25);
}

.hero h1 {
    font-size: 3.2rem;
    color: #1A1207;
    margin: 0;
    font-weight: 700;
    letter-spacing: -2px;
}

.hero p {
    color: #3D2B00;
    margin-top: 0.7rem;
    font-size: 1.08rem;
    font-weight: 500;
}

/* ─────────────────────────────────────────────────────────────
   TABS
───────────────────────────────────────────────────────────── */
div[data-baseweb="tab-list"] {
    gap: 40px;
    border-bottom: 1px solid #D5CCBC;
    margin-bottom: 2rem;
    background: transparent;
}

div[data-baseweb="tab-list"] button {
    font-size: 1rem;
    font-weight: 600;
    color: #6B5E4A;
    background: transparent;
    padding-bottom: 14px;
}

div[data-baseweb="tab-list"] button[aria-selected="true"] {
    color: #B8860B;
    border-bottom: 3px solid #D4A017;
}

/* ─────────────────────────────────────────────────────────────
   CARDS
───────────────────────────────────────────────────────────── */
.score-card {
    background: white;
    border: 1px solid #E5DCCC;
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.05);
}

.score-card:hover {
    transform: translateY(-2px);
    transition: 0.2s ease;
}

/* ─────────────────────────────────────────────────────────────
   SCORE BADGES
───────────────────────────────────────────────────────────── */
.score-badge {
    font-size: 2rem;
    font-weight: 700;
    color: #1A1207;
}

.rec-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    margin-top: 0.4rem;
}

.rec-HIRE   { background: #DCFCE7; color: #166534; }
.rec-MAYBE  { background: #FEF3C7; color: #92400E; }
.rec-NOHIRE { background: #FEE2E2; color: #991B1B; }

/* ─────────────────────────────────────────────────────────────
   DIMENSION BARS  — mustard yellow fill
───────────────────────────────────────────────────────────── */
.dim-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 10px 0;
}

.dim-label {
    width: 180px;
    font-size: 0.92rem;
    font-weight: 500;
    color: #3D2B00;
}

.dim-bar-bg {
    flex: 1;
    background: #EDE8DF;
    border-radius: 999px;
    overflow: hidden;
    height: 10px;
}

.dim-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #D4A017, #F0C040);
}

.dim-score {
    width: 50px;
    text-align: right;
    font-weight: 700;
    color: #1A1207;
}

/* ─────────────────────────────────────────────────────────────
   XAI BOX
───────────────────────────────────────────────────────────── */
.xai-box {
    background: #FFFBEF;
    border: 1px solid #E8CC80;
    border-radius: 18px;
    padding: 1.2rem;
    margin-top: 1rem;
}

.xai-title {
    color: #7A5C00;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* ─────────────────────────────────────────────────────────────
   BUTTONS  — mustard yellow
───────────────────────────────────────────────────────────── */
.stButton > button {
    background: #D4A017;
    color: #1A1207;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    padding: 0.55rem 1.6rem;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #B8860B;
    transform: translateY(-1px);
    color: #1A1207;
}

/* ─────────────────────────────────────────────────────────────
   METRICS
───────────────────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: white;
    border-radius: 16px;
    padding: 1rem;
    border: 1px solid #E5DCCC;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}

[data-testid="metric-container"] * {
    color: #1A1207 !important;
}

/* ─────────────────────────────────────────────────────────────
   FILE UPLOADER
───────────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    border: 2px dashed #C9B99A;
    border-radius: 16px;
    padding: 0.8rem;
    background: white;
}

/* ─────────────────────────────────────────────────────────────
   INPUTS
───────────────────────────────────────────────────────────── */
.stTextArea textarea,
.stTextInput input {
    background: white !important;
    color: #1A1207 !important;
    border-radius: 12px !important;
    border: 1px solid #C9B99A !important;
}

/* ─────────────────────────────────────────────────────────────
   PROGRESS BAR  — mustard
───────────────────────────────────────────────────────────── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #D4A017, #F0C040);
}

/* ─────────────────────────────────────────────────────────────
   SECURITY TABLE
───────────────────────────────────────────────────────────── */
.security-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    background: white;
    border-radius: 12px;
    overflow: hidden;
}

.security-table th {
    background: #D4A017;
    color: #1A1207;
    padding: 12px;
    text-align: left;
    font-weight: 700;
}

.security-table td {
    padding: 12px;
    border-bottom: 1px solid #F0E8D8;
    vertical-align: top;
    color: #1A1207;
}

.security-table tr:hover td {
    background: #FFFBEF;
}

/* ─────────────────────────────────────────────────────────────
   OVERRIDE PREVIEW BOX
───────────────────────────────────────────────────────────── */
.preview-box {
    background: #FFFBEF;
    border: 2px solid #D4A017;
    border-radius: 12px;
    padding: 1rem;
    margin-top: 1rem;
    color: #1A1207;
}

.preview-box h4 {
    color: #7A5C00;
    margin-bottom: 0.5rem;
}

/* ─────────────────────────────────────────────────────────────
   EXPANDER
───────────────────────────────────────────────────────────── */
details summary {
    color: #1A1207 !important;
}

/* ─────────────────────────────────────────────────────────────
   GENERAL TEXT OVERRIDES
───────────────────────────────────────────────────────────── */
p, span, label, div, h1, h2, h3, h4, small {
    color: #1A1207;
}

.stMarkdown, .stCaption {
    color: #4A3F2F !important;
}

code {
    background: #F0E8D8 !important;
    color: #3D2B00 !important;
    border-radius: 6px;
}

pre {
    background: #F0E8D8 !important;
    color: #3D2B00 !important;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Lazy import
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
    ("override_preview", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — minimal, no scoring table
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## HR Resume Shortlisting")
    st.markdown("---")

    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if api_key and not st.session_state.api_key_set:
        try:
            agents = get_agent_module()
            st.session_state.llm = agents["init_llm"](api_key)
            st.session_state.api_key_set = True
        except Exception as e:
            st.error(f"LLM init failed: {e}")
    # Stack info as clean chips, no table
    st.markdown("### Stack")
    st.markdown('<span class="sidebar-chip">Gemini 2.0 Flash</span>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-chip">LangChain LCEL</span>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-chip">LIME XAI</span>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-chip">SQLite Cache</span>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-chip">ReportLab PDF</span>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-chip">LangSmith / Langfuse</span>', unsafe_allow_html=True)


    # Scoring weights as simple text — no table
    st.markdown("### Scoring Weights")
    weights_md = """
| Dimension | Weight |
|---|---|
| Skills Match | **30%** |
| Experience | **25%** |
| Projects | **20%** |
| Education | **15%** |
| Communication | **10%** |
"""
    st.markdown(weights_md)


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>HR Resume Shortlisting</h1>
  <p>AI-powered resume shortlisting · Explainable scoring · Human-in-the-loop · Audit trail</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_run, tab_results, tab_xai, tab_override, tab_audit = st.tabs([
    "Run Agent", "Results", "XAI Insights", "Override Scores", "Audit Log"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Run Agent
# ══════════════════════════════════════════════════════════════════════════════
with tab_run:
    col_jd, col_resumes = st.columns([1, 1], gap="large")

    with col_jd:
        st.markdown("### Job Description")
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
                st.success(f"Loaded: {jd_file.name}")

    with col_resumes:
        st.markdown("### Candidate Resumes")
        resume_files_uploaded = st.file_uploader(
            "Upload resumes (PDF / DOCX / TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )
        if resume_files_uploaded:
            st.success(f"{len(resume_files_uploaded)} file(s) loaded")
            for f in resume_files_uploaded:
                st.caption(f"• {f.name}")

        st.markdown("#### LinkedIn JSON (optional)")
        linkedin_files_uploaded = st.file_uploader(
            "Upload exported LinkedIn JSON",
            type=["json"],
            accept_multiple_files=True,
        )

    st.markdown("---")

    col_btn1, col_btn2, _ = st.columns([1, 1, 3])

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
        "priya_sharma.txt": """
Priya Sharma | priya.sharma@email.com | Pune
SKILLS: Python, Pandas, Matplotlib, scikit-learn, SQL, Tableau, Git
EXPERIENCE: Junior Data Analyst — E-commerce Startup (2023–Present, 1.5 yrs)
- Customer segmentation analysis using K-Means
- Built dashboards tracking KPIs for marketing team
EDUCATION: B.Tech Computer Science — VJTI Mumbai (2022) 8.2 CGPA
CERTIFICATIONS: Google Data Analytics (2023)
PROJECTS:
1. E-commerce Recommendation System — Collaborative filtering
2. Sales Dashboard — Tableau integration with MySQL
""",
        "vikram_singh.txt": """
Vikram Singh | vikram.s@gmail.com | Hyderabad
SKILLS: Python, TensorFlow, Keras, OpenCV, Docker, Kubernetes, AWS SageMaker, Git, MLOps
EXPERIENCE: ML Engineer — AI Solutions Inc (2020–Present, 4 yrs)
- Computer vision model for defect detection, 96% accuracy
- Deployed 12+ models to production using CI/CD pipelines
- Optimized inference latency from 200ms to 35ms
EDUCATION: M.Tech AI/ML — IIIT Hyderabad (2020) CGPA 9.4
CERTIFICATIONS: AWS ML Specialty (2021), Kubernetes CKA (2022)
PROJECTS:
1. Real-time Object Detection — YOLO v5, edge deployment
2. Automated MLOps Pipeline — Jenkins + Docker + Kubernetes
3. NLP Chatbot — Transformer-based, 92% intent accuracy
"""
    }

    with col_btn1:
        use_sample = st.button("Load Sample Data", use_container_width=True)
    with col_btn2:
        run_btn = st.button("Run Agent", use_container_width=True)

    if use_sample:
        st.session_state["sample_jd"] = SAMPLE_JD
        st.session_state["sample_resumes"] = SAMPLE_RESUMES
        st.info("Sample data loaded - 5 candidates — click **Run Agent** to evaluate.")

if run_btn:

    agents = get_agent_module()

    active_jd = jd_text or st.session_state.get("sample_jd", "")

    if not active_jd.strip():
        st.error("Please provide a Job Description.")
        st.stop()

    tmp_dir = tempfile.mkdtemp()
    resume_paths = []

    # ─────────────────────────────────────────────
    # Uploaded resumes
    # ─────────────────────────────────────────────
    if resume_files_uploaded:

        for uf in resume_files_uploaded:

            path = os.path.join(tmp_dir, uf.name)

            with open(path, "wb") as f:
                f.write(uf.getvalue())

            resume_paths.append(path)

    # ─────────────────────────────────────────────
    # Sample resumes
    # ─────────────────────────────────────────────
    elif st.session_state.get("sample_resumes"):

        for fname, content in st.session_state["sample_resumes"].items():

            path = os.path.join(tmp_dir, fname)

            with open(path, "w") as f:
                f.write(content)

            resume_paths.append(path)

    # ─────────────────────────────────────────────
    # No resumes uploaded
    # ─────────────────────────────────────────────
    if not resume_paths:
        st.error("Please upload at least one resume.")
        st.stop()

    # ─────────────────────────────────────────────
    # LinkedIn JSON
    # ─────────────────────────────────────────────
    linkedin_paths = []

    for lf in (linkedin_files_uploaded or []):

        path = os.path.join(tmp_dir, lf.name)

        with open(path, "wb") as f:
            f.write(lf.getvalue())

        linkedin_paths.append(path)

    # ─────────────────────────────────────────────
    # Progress UI
    # ─────────────────────────────────────────────
    progress = st.progress(0, text="Starting agent…")
    status = st.empty()

    steps = [
        (15, "Parsing Job Description…"),
        (30, "Loading resumes…"),
        (55, "Extracting profiles & computing similarity…"),
        (75, "Scoring candidates…"),
        (90, "Generating XAI explanations…"),
        (98, "Creating PDF report…"),
    ]

    import time as _time

    for pct, msg in steps:
        progress.progress(pct, text=msg)
        _time.sleep(0.5)

    # ─────────────────────────────────────────────
    # Run Agent
    # ─────────────────────────────────────────────
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

    progress.progress(100, text="Done!")

    _time.sleep(0.5)

    progress.empty()
    status.empty()

    # ─────────────────────────────────────────────
    # Output
    # ─────────────────────────────────────────────
    if st.session_state.results:

        st.success(
            f"Evaluated {len(st.session_state.results)} candidates."
        )

        if os.path.exists("outputs/shortlist_report.pdf"):

            with open("outputs/shortlist_report.pdf", "rb") as f:

                st.download_button(
                    "Download PDF Report",
                    data=f,
                    file_name="hr_shortlist_report.pdf",
                    mime="application/pdf",
                )

    else:
        st.error("Agent returned no results.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Results
# ══════════════════════════════════════════════════════════════════════════════
with tab_results:
    if not st.session_state.results:
        st.info("Run the agent first (Run Agent tab).")
    else:
        results = st.session_state.results

        n_hire   = sum(1 for r in results if r["scores"]["recommendation"] == "HIRE")
        n_maybe  = sum(1 for r in results if r["scores"]["recommendation"] == "MAYBE")
        n_nohire = sum(1 for r in results if r["scores"]["recommendation"] == "NO HIRE")
        avg_score = sum(r["scores"]["total_score"] for r in results) / len(results)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Evaluated", len(results))
        c2.metric("HIRE",    n_hire)
        c3.metric("MAYBE",   n_maybe)
        c4.metric("NO HIRE", n_nohire)

        st.markdown("---")
        st.markdown("### Candidate Rankings")

        st.code("""
AGENT OUTPUT (Mandatory Format):
────────────────────────────────
For each candidate, the agent prints:
  • Dimension-level scores (0-10)
  • Weighted total score
  • One-line justification per dimension
────────────────────────────────
""")

        for r in results:
            name  = r["candidate_info"].get("name", "?")
            total = r["scores"]["total_score"]
            rec   = r["scores"]["recommendation"]
            rank  = r.get("rank", "?")
            sim   = r.get("embedding", {}).get("similarity_pct", "—")

            rec_badge_class = {"HIRE": "rec-HIRE", "MAYBE": "rec-MAYBE"}.get(rec, "rec-NOHIRE")

            with st.expander(f"#{rank}  {name}  —  {total}/10  ({rec})", expanded=(rank == 1)):
                col_score, col_info = st.columns([1, 2])

                with col_score:
                    st.markdown(
                        f'<div class="score-card">'
                        f'<div class="score-badge">{total}/10</div><br>'
                        f'<span class="rec-badge {rec_badge_class}">{rec}</span><br><br>'
                        f'<small>TF-IDF Similarity: <b>{sim}</b></small>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
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

                lime_feats = r.get("xai_features", [])
                contribs   = r.get("xai_contributions", [])
                if lime_feats or contribs:
                    st.markdown(
                        '<div class="xai-box"><div class="xai-title">XAI Insights</div>',
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

                col_s, col_c = st.columns(2)
                with col_s:
                    st.markdown("**Strengths**")
                    for s in r["scores"].get("strengths", []):
                        st.caption(f"• {s}")
                with col_c:
                    st.markdown("**Concerns**")
                    for c in r["scores"].get("concerns", []):
                        st.caption(f"• {c}")

        st.markdown("---")
        col_dl1, col_dl2, _ = st.columns([1, 1, 3])
        with col_dl1:
            if os.path.exists("outputs/shortlist_report.pdf"):
                with open("outputs/shortlist_report.pdf", "rb") as f:
                    st.download_button("Download PDF Report", f, "hr_report.pdf", "application/pdf")
        with col_dl2:
            if os.path.exists("outputs/scored_candidates.json"):
                with open("outputs/scored_candidates.json") as f:
                    st.download_button("Download JSON Data", f, "scored_candidates.json", "application/json")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — XAI Insights  (rich graphs & plots)
# ══════════════════════════════════════════════════════════════════════════════
MUSTARD   = "#D4A017"
GOLD_DARK = "#B8860B"
CREAM     = "#F5F1EA"
WHITE     = "#FFFFFF"
TEXT      = "#000000"

MUSTARD_SCALE = [
    [0.0,  "#FEE2E2"],   # red-ish (low)
    [0.4,  "#FFF9C4"],   # amber (mid)
    [0.7,  "#FDE68A"],   # yellow
    [1.0,  "#FFF59D"],   # mustard (high)
]

def make_plotly_layout(title="", height=400):
    return dict(
        title=dict(text=title, font=dict(family="Inter", size=16, color=TEXT)),
        plot_bgcolor=WHITE,
        paper_bgcolor=WHITE,
        font=dict(family="Inter", size=13, color=TEXT),
        margin=dict(l=20, r=20, t=50 if title else 20, b=20),
        height=height,
        xaxis=dict(tickfont=dict(color="#000000"), title_font=dict(color="#000000")),
        yaxis=dict(tickfont=dict(color="#000000"), title_font=dict(color="#000000")),
    )

with tab_xai:
    st.markdown("## Explainable AI Insights")

    if not st.session_state.results:
        st.info("Run evaluation first to see XAI visualizations.")
    else:
        import pandas as pd

        results = st.session_state.results

        # ── 1. Overview: Grouped bar — all candidates × all dimensions ──────
        st.markdown("### Dimension Scores — All Candidates")
        rows = []
        for r in results:
            name = r["candidate_info"].get("name", "?")
            for d in r["scores"]["dimension_scores"]:
                rows.append({
                    "Candidate": name.split()[0],   # first name only for legibility
                    "Dimension": d["dimension"],
                    "Score": d["score"],
                })
        df_all = pd.DataFrame(rows)

        fig_grouped = px.bar(
            df_all,
            x="Candidate",
            y="Score",
            color="Dimension",
            barmode="group",
            text="Score",
            color_discrete_sequence=["#FFF9C4", "#FFF59D", "#FFF176", "#FFEE58", "#FDD835"],
            height=420,
        )
        fig_grouped.update_layout(**make_plotly_layout(height=420))
        fig_grouped.update_traces(textposition="outside", textfont_size=11)
        fig_grouped.update_yaxes(range=[0, 11])
        st.plotly_chart(fig_grouped, use_container_width=True)

        # ── 2. Heatmap — candidates × dimensions ────────────────────────────
        st.markdown("### Score Heatmap")
        pivot = df_all.pivot(index="Candidate", columns="Dimension", values="Score")
        fig_heat = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[
                [0,   "#FEE2E2"],
                [0.4, "#FEF3C7"],
                [0.7, "#FDE68A"],
                [1,   "#D4A017"],
            ],
            zmin=0, zmax=10,
            text=[[f"{v:.1f}" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            hoverongaps=False,
        ))
        fig_heat.update_layout(**make_plotly_layout(height=320))
        st.plotly_chart(fig_heat, use_container_width=True)

        # ── 3. Total score bar + recommendation colour ───────────────────────
        st.markdown("### Overall Ranking")
        tot_data = sorted(
            [{"Name": r["candidate_info"].get("name","?"),
              "Score": r["scores"]["total_score"],
              "Rec": r["scores"]["recommendation"]} for r in results],
            key=lambda x: x["Score"], reverse=True
        )
        df_tot = pd.DataFrame(tot_data)
        color_map = {"HIRE": "#22C55E", "MAYBE": "#F59E0B", "NO HIRE": "#EF4444"}
        df_tot["Color"] = df_tot["Rec"].map(color_map)

        fig_rank = go.Figure(go.Bar(
            x=df_tot["Name"],
            y=df_tot["Score"],
            marker_color=df_tot["Color"],
            text=df_tot["Score"],
            textposition="outside",
        ))
        fig_rank.update_layout(**make_plotly_layout("Candidates ranked by total score", height=380))
        fig_rank.update_yaxes(range=[0, 11])
        st.plotly_chart(fig_rank, use_container_width=True)

        # ── 4. Per-candidate radar + LIME bar ───────────────────────────────
        st.markdown("### Per-Candidate Deep Dive")

        for idx, cand in enumerate(results):
            name = cand["candidate_info"].get("name", f"Candidate {idx+1}")
            rec  = cand["scores"]["recommendation"]
            total = cand["scores"]["total_score"]

            badge_color = {"HIRE": "#22C55E", "MAYBE": "#F59E0B"}.get(rec, "#EF4444")

            st.markdown(
                f'<h4 style="color:{TEXT};">{name} &nbsp;'
                f'<span style="background:{badge_color};color:white;'
                f'padding:3px 12px;border-radius:999px;font-size:0.8rem;">{rec}</span>'
                f'&nbsp; <span style="color:#7A5C00;">Score: {total}/10</span></h4>',
                unsafe_allow_html=True,
            )

            col_radar, col_bar = st.columns(2)

            dims    = [d["dimension"] for d in cand["scores"]["dimension_scores"]]
            scores  = [d["score"]     for d in cand["scores"]["dimension_scores"]]

            # Radar
            with col_radar:
                fig_radar = go.Figure(go.Scatterpolar(
                    r=scores + [scores[0]],
                    theta=dims + [dims[0]],
                    fill="toself",
                    fillcolor=f"rgba(212,160,23,0.25)",
                    line=dict(color=MUSTARD, width=2),
                    name=name,
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 10],
                                        tickfont=dict(color=TEXT, size=10),
                                        gridcolor="#E5DCCC"),
                        angularaxis=dict(tickfont=dict(color=TEXT, size=11)),
                        bgcolor=WHITE,
                    ),
                    showlegend=False,
                    height=340,
                    paper_bgcolor=WHITE,
                    margin=dict(l=40, r=40, t=20, b=20),
                    font=dict(family="Inter", color=TEXT),
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            # Horizontal bar per dimension
            with col_bar:
                df_dim = pd.DataFrame({"Dimension": dims, "Score": scores})
                fig_hbar = px.bar(
                    df_dim,
                    x="Score", y="Dimension",
                    orientation="h",
                    text="Score",
                    color="Score",
                    color_continuous_scale=MUSTARD_SCALE,
                    range_color=[0, 10],
                    height=340,
                )
                fig_hbar.update_layout(**make_plotly_layout(height=340))
                fig_hbar.update_coloraxes(showscale=False)
                fig_hbar.update_traces(textposition="outside")
                fig_hbar.update_xaxes(range=[0, 12])
                st.plotly_chart(fig_hbar, use_container_width=True)

            # Justification table
            with st.expander("Dimension justifications"):
                for d in cand["scores"]["dimension_scores"]:
                    st.markdown(f"**{d['dimension']}** ({d['score']}/10) — {d['justification']}")

            st.divider()




# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Human Override
# ══════════════════════════════════════════════════════════════════════════════
with tab_override:
    st.markdown("### Human-in-the-Loop Score Override")
    st.markdown(
        "Adjust any dimension score after AI evaluation. "
        "Every change is permanently logged to **audit_log.json**."
    )

    if not st.session_state.results:
        st.info("Run the agent first to enable overrides.")
    else:
        names = [r["candidate_info"]["name"] for r in st.session_state.results]
        c_name = st.selectbox("Select Candidate", names)

        current_cand = next((r for r in st.session_state.results
                             if r["candidate_info"]["name"] == c_name), None)

        dimension = st.selectbox(
            "Dimension to Override",
            ["Skills Match", "Experience", "Education & Certs", "Projects", "Communication"],
        )

        current_score = 5.0
        if current_cand:
            for d in current_cand["scores"]["dimension_scores"]:
                if d["dimension"] == dimension:
                    current_score = d["score"]
                    break

        new_score = st.slider(
            "New Score", 0.0, 10.0, float(current_score), 0.5,
            key="override_slider"
        )

        if current_cand and new_score != current_score:
            weights_map = {
                "Skills Match": 0.30, "Experience": 0.25,
                "Education & Certs": 0.15, "Projects": 0.20, "Communication": 0.10,
            }
            old_total = current_cand["scores"]["total_score"]
            new_total = sum(
                (new_score if d["dimension"] == dimension else d["score"])
                * weights_map.get(d["dimension"], 0.1)
                for d in current_cand["scores"]["dimension_scores"]
            )
            st.markdown(
                f"""<div class="preview-box">
                    <h4>Preview Score Change</h4>
                    <p><strong>{dimension}:</strong> {current_score}/10 → {new_score}/10</p>
                    <p><strong>Total Score:</strong> {old_total:.2f}/10 → {new_total:.2f}/10</p>
                    <p><strong>Change:</strong> {new_total - old_total:+.2f} points</p>
                </div>""",
                unsafe_allow_html=True
            )

        reason   = st.text_input("Reason for override", placeholder="e.g. Strong GitHub portfolio shown at interview")
        reviewer = st.text_input("Reviewer name", value="HR Manager")

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
                st.success(f"Score updated for {c_name} — {dimension}: {new_score}/10")
                if st.session_state.results:
                    agents["generate_pdf_report"](
                        st.session_state.results,
                        st.session_state.get("jd_parsed", {}),
                    )
                    st.caption("PDF report regenerated with override applied.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — Audit Log
# ══════════════════════════════════════════════════════════════════════════════
with tab_audit:
    st.markdown("### Audit Trail")
    st.caption("Every agent action is logged here and written to audit_log.json on disk.")

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
            st.download_button(
                "Download Audit Log",
                open(log_path).read(),
                "audit_log.json",
                "application/json"
            )
        else:
            st.info("Audit log is empty.")
    else:
        st.info("No audit log yet. Run the agent to generate one.")
