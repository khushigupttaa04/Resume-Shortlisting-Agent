# ── Stdlib ────────────────────────────────────────────────────────────────────
import os, re, json, logging, time
from datetime import datetime
from typing import List, Dict, Optional

# ── Document parsing ──────────────────────────────────────────────────────────
import pypdf
from docx import Document as DocxDocument

# ── Data / ML ─────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── XAI ───────────────────────────────────────────────────────────────────────
import lime
import lime.lime_text

# ── LangChain LCEL ────────────────────────────────────────────────────────────
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.globals import set_llm_cache
from langchain_community.cache import SQLiteCache

# ── PDF report ────────────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable, PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
pip install kaleido
import plotly.io as pio

DELAY_BETWEEN_CANDIDATES = 4   # gemini free-tier RPM

# Brand palette
C_NAVY   = colors.HexColor("#1B3A6B")
C_TEAL   = colors.HexColor("#0D9488")
C_AMBER  = colors.HexColor("#F59E0B")
C_PURPLE = colors.HexColor("#7C3AED")
C_LGRAY  = colors.HexColor("#F3F4F6")
C_DGRAY  = colors.HexColor("#374151")

# AUDIT LOGGER  

logging.basicConfig(
    filename="audit_log.txt",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)

def audit(event: str, detail: str = "") -> None:
    """Append a structured entry to audit_log.json + audit_log.txt."""
    entry = {"timestamp": datetime.now().isoformat(), "event": event, "detail": detail}
    logging.info(f"{event} | {detail}")
    with open("audit_log.json", "a") as f:
        f.write(json.dumps(entry) + "\n")


# PII MASKING   avoid write raw emails/phones to logs
def mask_pii(text: str) -> str:
    """Mask emails and phone numbers before writing to any log."""
    # email: first char + **** + domain
    text = re.sub(
        r"([\w.+-])([\w.+-]+)(@[\w-]+\.[a-zA-Z]+)",
        lambda m: m.group(1) + "****" + m.group(3),
        text,
    )
    text = re.sub(r"\b(\+?\d[\d\s\-]{7,}\d)\b", "[PHONE]", text)
    return text


# LLM SETUP  (LangChain + SQLite caching)

def init_llm(api_key: str) -> ChatGoogleGenerativeAI:
    """Initialise Gemini via LangChain with SQLite response caching."""
    os.environ["GOOGLE_API_KEY"] = api_key
    set_llm_cache(SQLiteCache(database_path="llm_cache.db"))
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        google_api_key=api_key,
        temperature=0,
        max_tokens=2048,
        max_retries=3,
    )
    audit("LLM_INIT", "model=gemini-2.5-flash | cache=SQLite")
    return llm


# DOCUMENT READERS
def read_pdf(path: str, max_mb: int = 10) -> str:
    assert os.path.getsize(path) / 1e6 <= max_mb, f"PDF > {max_mb} MB"
    text = ""
    with open(path, "rb") as f:
        for page in pypdf.PdfReader(f).pages:
            text += page.extract_text() or ""
    return text.strip()


def read_docx(path: str, max_mb: int = 10) -> str:
    assert os.path.getsize(path) / 1e6 <= max_mb, f"DOCX > {max_mb} MB"
    doc = DocxDocument(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            paragraphs.append(" | ".join(c.text for c in row.cells))
    return "\n".join(paragraphs)


def read_resume(path: str) -> str:
    """Universal reader: PDF / DOCX / TXT."""
    ext = path.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return read_pdf(path)
    elif ext in ("docx", "doc"):
        return read_docx(path)
    elif ext == "txt":
        with open(path, encoding="utf-8") as f:
            return f.read()
    raise ValueError(f"Unsupported format: .{ext}")


def read_linkedin_json(path: str) -> str:
    """Convert exported LinkedIn JSON to plain text for the pipeline."""
    with open(path) as f:
        d = json.load(f)
    name  = f"{d.get('firstName','')} {d.get('lastName','')}".strip()
    skills = ", ".join(d.get("skills", []))
    certs  = ", ".join(d.get("certifications", []))
    summary = d.get("summary", "")
    exp_text = ""
    for p in d.get("positions", []):
        s = p.get("startDate", {}).get("year", "")
        e = p.get("endDate", {}).get("year", "Present") if p.get("endDate") else "Present"
        exp_text += f"\n- {p.get('title')} at {p.get('companyName')} ({s}–{e}): {p.get('description','')}"
    edu_text = ""
    for e in d.get("educations", []):
        edu_text += f"\n- {e.get('degreeName','')} in {e.get('fieldOfStudy','')} from {e.get('schoolName','')}"
    return (
        f"Name: {name}\nSummary: {summary}\nSkills: {skills}\n"
        f"Certifications: {certs}\nExperience:{exp_text}\nEducation:{edu_text}\n"
        f"Source: LinkedIn Profile"
    )


# JD PARSER  (LangChain LCEL)

_JD_PROMPT = PromptTemplate(
    input_variables=["jd_text"],
    template="""You are an expert HR analyst. Extract structured requirements.

Job Description:
{jd_text}

Return ONLY valid JSON — no markdown, no explanation:
{{
  "role_title": "exact job title",
  "required_skills": ["skill1", "skill2"],
  "nice_to_have": ["skill1"],
  "min_experience": 2,
  "max_experience": 5,
  "required_education": "B.Tech/M.Tech in CS or related",
  "domain": "fintech",
  "seniority": "Senior"
}}

JSON:""",
)

def analyze_jd(jd_text: str, llm) -> dict:
    """Parse JD → structured requirements dict. Cached in SQLite."""
    chain = _JD_PROMPT | llm | StrOutputParser()
    raw = chain.invoke({"jd_text": jd_text})
    raw = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        result = json.loads(raw)
        audit("JD_PARSED", f"role={result.get('role_title')} skills={len(result.get('required_skills',[]))}")
        return result
    except json.JSONDecodeError:
        audit("JD_PARSE_ERROR", raw[:120])
        return {"role_title": "Unknown", "required_skills": [], "nice_to_have": [],
                "min_experience": 0, "domain": "General", "seniority": "Mid",
                "required_education": "Bachelor's Degree"}



# CANDIDATE PROFILER  (LangChain LCEL)

_PROFILE_PROMPT = PromptTemplate(
    input_variables=["resume_text"],
    template="""Extract candidate information from this resume.

Resume:
{resume_text}

Return ONLY valid JSON:
{{
  "name": "Full Name",
  "email": "email or null",
  "skills": ["skill1", "skill2"],
  "total_experience": 3.5,
  "education": ["degree, institution, year"],
  "certifications": ["cert1"],
  "work_history": [{{"company": "", "role": "", "duration": "", "domain": ""}}],
  "projects": ["project description"],
  "summary": "one-line summary"
}}

JSON:""",
)

def extract_candidate(resume_text: str, llm) -> dict:
    chain = _PROFILE_PROMPT | llm | StrOutputParser()
    raw = chain.invoke({"resume_text": resume_text[:4000]})
    raw = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {"name": "Unknown", "email": None, "skills": [],
                "total_experience": 0, "education": [], "certifications": [],
                "work_history": [], "projects": [], "summary": ""}


# SKILL MATCHER  (TF-IDF + keyword overlap)

from difflib import SequenceMatcher


def fuzzy_match(skill: str, text: str, threshold: float = 0.75) -> bool:
    """
    General fuzzy semantic-ish matching.

    Detects:
    - NLP ↔ Natural Language Processing
    - ML ↔ Machine Learning
    - APIs ↔ REST API
    - PyTorch ↔ torch
    etc.
    """

    skill = skill.lower().strip()
    text = text.lower()

    # direct match
    if skill in text:
        return True

    words = re.findall(r'\w+', text)

    # fuzzy token matching
    for word in words:

        ratio = SequenceMatcher(
            None,
            skill,
            word
        ).ratio()

        if ratio >= threshold:
            return True

    # acronym detection
    acronym = "".join(w[0] for w in skill.split() if w)

    if acronym and acronym.lower() in text:
        return True

    return False


def calculate_skill_match(candidate_text: str, required_skills: list) -> dict:

    matched = []
    missing = []

    for skill in required_skills:

        if fuzzy_match(skill, candidate_text):
            matched.append(skill)

        else:
            missing.append(skill)

    pct = round(
        len(matched) / max(len(required_skills), 1) * 100,
        1
    )

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_pct": pct,
        "match_summary": f"{len(matched)}/{len(required_skills)} ({pct}%)"
    }

def compute_tfidf_similarity(candidate: dict, jd: dict) -> dict:
    """
    Cosine similarity between candidate text and JD skills.
    """

    cand_text = (
        " ".join(candidate.get("skills", []))
        + " "
        + candidate.get("summary", "")
    )

    jd_text = " ".join(
        jd.get("required_skills", [])
        + jd.get("nice_to_have", [])
    )

    if not cand_text.strip() or not jd_text.strip():
        return {
            "similarity": 0.0,
            "similarity_pct": "0.0%"
        }

    vec = TfidfVectorizer().fit_transform([
        cand_text,
        jd_text
    ])

    score = round(
        float(
            cosine_similarity(vec[0], vec[1])[0][0]
        ) * 100,
        1
    )

    return {
        "similarity": score / 100,
        "similarity_pct": f"{score}%"
    }
    
# 5-DIMENSION SCORER  (LangChain LCEL)
_SCORE_PROMPT = PromptTemplate(
    input_variables=["candidate_json", "jd_json", "skill_summary"],
    template="""You are an expert HR evaluator. Score this candidate strictly.

CANDIDATE:
{candidate_json}

JOB REQUIREMENTS:
{jd_json}

SKILL ANALYSIS:
{skill_summary}

SCORING RUBRIC (0–10):
1. Skills Match      (30%) — 0–3: <30% match | 4–6: 50–70% | 7–10: >85%
2. Experience        (25%) — 0–3: wrong domain | 4–6: adjacent | 7–10: exact fit
3. Education & Certs (15%) — 0–3: below min | 4–6: meets | 7–10: exceeds+certs
4. Projects          (20%) — 0–3: none | 4–6: 1–2 generic | 7–10: strong portfolio
5. Communication     (10%) — 0–3: poor | 4–6: adequate | 7–10: crisp+structured

Return ONLY valid JSON:
{{
  "dimension_scores": [
    {{"dimension": "Skills Match",      "score": 8, "weight": 0.30, "justification": "..."}},
    {{"dimension": "Experience",        "score": 7, "weight": 0.25, "justification": "..."}},
    {{"dimension": "Education & Certs", "score": 9, "weight": 0.15, "justification": "..."}},
    {{"dimension": "Projects",          "score": 8, "weight": 0.20, "justification": "..."}},
    {{"dimension": "Communication",     "score": 8, "weight": 0.10, "justification": "..."}}
  ],
  "strengths": ["strength 1", "strength 2"],
  "concerns":  ["concern 1"],
  "skill_gap": ["missing skill 1"]
}}

JSON:""",
)

def score_candidate(candidate: dict, jd: dict, skill_match: dict, llm) -> Optional[dict]:
    chain = _SCORE_PROMPT | llm | StrOutputParser()
    raw = chain.invoke({
        "candidate_json": json.dumps({k: candidate[k] for k in
            ("name","skills","total_experience","education","certifications","projects","summary")
            if k in candidate}, indent=2)[:1500],
        "jd_json": json.dumps({k: jd[k] for k in
            ("role_title","required_skills","min_experience","domain","seniority")
            if k in jd}, indent=2),
        "skill_summary": (
            f"Match: {skill_match['match_summary']} | "
            f"Missing: {', '.join(skill_match['missing_skills'][:5])}"
        ),
    })
    raw = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        scores = json.loads(raw)
        total = sum(d["score"] * d["weight"] for d in scores["dimension_scores"])
        scores["total_score"] = round(total, 2)
        scores["recommendation"] = (
            "HIRE"    if total >= 7.0 else
            "MAYBE"   if total >= 4.5 else
            "NO HIRE"
        )
        audit("CANDIDATE_SCORED",
              f"name={candidate.get('name')} score={scores['total_score']} rec={scores['recommendation']}")
        return scores
    except Exception as e:
        audit("SCORE_ERROR", str(e))
        return None


# XAI — LIME + Dimension contributions

def explain_with_lime(resume_text: str, required_skills: list, top_n: int = 6) -> list:
    """LIME explanation: which keywords most influenced the skill-match score."""
    explainer = lime.lime_text.LimeTextExplainer(class_names=["Low Fit", "High Fit"])

    def predict(texts):
        out = []
        for t in texts:
            cnt = sum(1 for s in required_skills if s.lower() in t.lower())
            p = min(cnt / max(len(required_skills), 1), 1.0)
            out.append([1 - p, p])
        return np.array(out)

    try:
        exp = explainer.explain_instance(resume_text, predict, num_features=top_n, labels=(1,))
        return exp.as_list(label=1)
    except Exception:
        return []


def explain_dimension_contributions(scores: dict) -> list:
    """Show how much each dimension pushed the score above/below the 5.0 baseline."""
    baseline = 5.0
    contribs = []
    for d in scores.get("dimension_scores", []):
        contribs.append({
            "dimension":    d["dimension"],
            "contribution": round((d["score"] - baseline) * d["weight"], 3),
        })
    return contribs


# HUMAN-IN-THE-LOOP OVERRIDE
VALID_DIMENSIONS = {"Skills Match", "Experience", "Education & Certs", "Projects", "Communication"}

def override_score(
    results: list,
    candidate_name: str,
    dimension: str,
    new_score: float,
    reason: str,
    reviewer: str = "HR Manager",
) -> list:
    """
    Let HR adjust any dimension score post-evaluation.
    Every change is permanently written to audit_log.json.
    """
    if dimension not in VALID_DIMENSIONS:
        print(f"❌ Invalid dimension. Choose from: {VALID_DIMENSIONS}")
        return results
    if not 0 <= new_score <= 10:
        print("❌ Score must be 0–10.")
        return results

    for r in results:
        if r["candidate_info"]["name"].lower() == candidate_name.lower():
            for d in r["scores"]["dimension_scores"]:
                if d["dimension"] == dimension:
                    original = d["score"]
                    d["score"] = new_score
                    d["justification"] += f" [OVERRIDDEN by {reviewer}: {reason}]"
                    new_total = sum(x["score"] * x["weight"] for x in r["scores"]["dimension_scores"])
                    r["scores"]["total_score"] = round(new_total, 2)
                    r["scores"]["recommendation"] = (
                        "HIRE" if new_total >= 7.0 else "MAYBE" if new_total >= 4.5 else "NO HIRE"
                    )
                    results.sort(key=lambda x: x["scores"]["total_score"], reverse=True)
                    audit("HR_OVERRIDE",
                          f"reviewer={reviewer} candidate={candidate_name} "
                          f"dim={dimension} {original}→{new_score} reason={reason}")
                    print(f"✅ Override logged | {candidate_name} | {dimension}: {original} → {new_score}")
                    return results
    print(f"❌ Candidate '{candidate_name}' not found.")
    return results


# PDF REPORT GENERATOR

def generate_pdf_report(results: list, jd: dict, path: str = "outputs/shortlist_report.pdf") -> str:
    """
    Professional B&W ReportLab PDF with Table and XAI Graph Support.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    os.makedirs("temp_plots", exist_ok=True) # Storage for static graph images
    
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        topMargin=1.2*cm, bottomMargin=1.2*cm,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # ── BLACK & WHITE THEME STYLES ──────────────────────────────────────────
    def sty(name, **kw):
        return ParagraphStyle(name, **kw)

    T_TITLE = sty("T", fontSize=22, fontName="Helvetica-Bold", textColor=colors.black, alignment=TA_CENTER, spaceAfter=10)
    T_SEC   = sty("SEC", fontSize=14, fontName="Helvetica-Bold", textColor=colors.black, spaceBefore=15, spaceAfter=10)
    T_BODY  = sty("BD", fontSize=9, leading=12, textColor=colors.black)
    T_SUB   = sty("S", fontSize=8, textColor=colors.grey, alignment=TA_CENTER)

    # ── COVER PAGE ──────────────────────────────────────────────────────────
    story += [
        Spacer(1, 2*cm),
        Paragraph("HR SHORTLIST REPORT", T_TITLE),
        HRFlowable(width="100%", thickness=1, color=colors.black),
        Spacer(1, 0.5*cm),
        Paragraph(f"Role: {jd.get('role_title','N/A')} | Total Candidates: {len(results)}", T_SUB),
        Paragraph(f"Report Date: {datetime.now().strftime('%d %b %Y %H:%M')}", T_SUB),
        Spacer(1, 1*cm),
    ]

    # ── RANKED SUMMARY TABLE ────────────────────────────────────────────────
    story.append(Paragraph("Candidate Rankings & Decisions", T_SEC))
    
    hdr = [["Rank", "Candidate", "Similarity", "Total Score", "Decision"]]
    rows = hdr.copy()
    
    for i, r in enumerate(results, 1):
        rows.append([
            str(i),
            r["candidate_info"].get("name","?"),
            r.get("embedding", {}).get("similarity_pct", "—"),
            f"{r['scores']['total_score']}/10",
            r["scores"]["recommendation"]
        ])

    tbl = Table(rows, colWidths=[1.5*cm, 6*cm, 2.5*cm, 3*cm, 4*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.black),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
    ]))
    story += [tbl, PageBreak()]

    # ── XAI GRAPHS SECTION ──────────────────────────────────────────────────
    import streamlit as st
    story.append(Paragraph("Executive Visualization", T_SEC))
    
    # Loop through the global charts we saved in app.py
    for fig_key in ["fig_overall", "fig_heat"]:
        if fig_key in st.session_state:
            img_path = f"temp_plots/{fig_key}.png"
            st.session_state[fig_key].write_image(img_path, engine="kaleido", width=800, height=400, scale=2)
            story.append(Image(img_path, width=16*cm, height=8*cm))
            story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # ── PER-CANDIDATE DETAIL ───────────────────────────────────────────────
    for r in results:
        name = r["candidate_info"].get("name", "?")
        story.append(Paragraph(f"Detailed Evaluation: {name}", T_SEC))
        fig_key = f"fig_chart_{name}"
        if fig_key in st.session_state:
            img_path = f"temp_plots/chart_{name.replace(' ', '_')}.png"
            st.session_state[fig_key].write_image(img_path, engine="kaleido", width=700, height=350)
            story.append(Image(img_path, width=14*cm, height=7*cm))
            story.append(Spacer(1, 0.5*cm))
        # Scoring Table
        dim_rows = [["Dimension", "Score", "Justification"]]
        for d in r["scores"]["dimension_scores"]:
            # Truncate justification for table fit
            just = d["justification"]
            short_just = (just[:120] + '...') if len(just) > 120 else just
            dim_rows.append([d["dimension"], f"{d['score']}/10", short_just])
            
        dt = Table(dim_rows, colWidths=[4*cm, 2*cm, 11*cm])
        dt.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("FONTSIZE", (0,0), (-1,-1), 8.5),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story += [dt, Spacer(1, 0.5*cm)]

    doc.build(story)
    audit("REPORT_GENERATED", f"path={path}")
    return path

# MAIN AGENT PIPELINE
def run_agent(
    jd_text: str,
    resume_files: List[str] = None,
    linkedin_files: List[str] = None,
    llm=None,
    generate_report: bool = True,
    report_path: str = "outputs/shortlist_report.pdf",
) -> List[dict]:
    """
    Full 7-step HR Shortlisting Agent pipeline.

    Architecture: Sequential Plan-and-Execute (LangChain LCEL)
      1  Parse JD          → LangChain LCEL chain
      2  Ingest profiles   → PDF / DOCX / TXT / LinkedIn JSON
      3  Semantic match    → TF-IDF cosine + keyword overlap
      4  LLM scoring       → 5-dimension rubric via LCEL
      5  XAI               → LIME + dimension contributions
      6  Rank              → sort by total_score desc
      7  Report            → PDF + JSON

    Caching: SQLite (llm_cache.db) — zero API calls for repeated prompts.
    """
    resume_files   = resume_files   or []
    linkedin_files = linkedin_files or []

    print("\n" + "="*62)
    print("  TALENTMATCH AI  |  Gemini 2.5 Flash  |  LangChain LCEL")
    print("="*62)

    # Step 1 — Parse JD
    print("\n[1/7] Parsing Job Description…")
    jd = analyze_jd(jd_text, llm)
    print(f"   ✓ Role: {jd.get('role_title')}  |  Skills: {len(jd.get('required_skills',[]))}")

    # Step 2 — Load candidates
    print(f"\n[2/7] Loading candidates ({len(resume_files)} resumes, {len(linkedin_files)} LinkedIn)…")
    all_profiles = []
    for path in resume_files:
        try:
            text = read_resume(path)
            all_profiles.append((text, path, "resume"))
            print(f"   ✓ {os.path.basename(path)}")
        except Exception as e:
            print(f"   ✗ {path}: {e}")
    for path in linkedin_files:
        try:
            text = read_linkedin_json(path)
            all_profiles.append((text, path, "linkedin"))
            print(f"   ✓ LinkedIn: {os.path.basename(path)}")
        except Exception as e:
            print(f"   ✗ {path}: {e}")

    if not all_profiles:
        print("❌ No candidates loaded.")
        return []

    # Steps 3–5 — Per-candidate processing
    print(f"\n[3–5/7] Processing {len(all_profiles)} candidate(s)…")
    results = []
    for i, (text, path, source) in enumerate(all_profiles, 1):
        print(f"\n  ── Candidate {i}/{len(all_profiles)} ──")
        candidate = extract_candidate(text, llm)
        candidate["source"] = source
        candidate["file"]   = os.path.basename(path)

        embedding   = compute_tfidf_similarity(candidate, jd)

        candidate_blob = (
            " ".join(candidate.get("skills", []))
            + " "
            + text
        )

        skill_match = calculate_skill_match(
            candidate_blob,
            jd.get("required_skills", [])
        )
        print(f"   Similarity: {embedding['similarity_pct']}  |  Skills: {skill_match['match_summary']}")

        scores = score_candidate(candidate, jd, skill_match, llm)
        if scores is None:
            continue

        lime_feats    = explain_with_lime(text, jd.get("required_skills", []))
        contributions = explain_dimension_contributions(scores)

        results.append({
            "candidate_info":    candidate,
            "skill_match":       skill_match,
            "embedding":         embedding,
            "scores":            scores,
            "xai_features":      lime_feats,
            "xai_contributions": contributions,
        })
        if i < len(all_profiles):
            time.sleep(DELAY_BETWEEN_CANDIDATES)

    if not results:
        print("❌ No candidates scored.")
        return []

    # Step 6 — Rank
    print("\n[6/7] Ranking…")
    results.sort(key=lambda x: x["scores"]["total_score"], reverse=True)
    for i, r in enumerate(results, 1):
        r["rank"] = i

    # Step 7 — Output
    print("\n[7/7] Generating outputs…")
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/scored_candidates.json", "w") as f:
        json.dump(results, f, default=str, indent=2)
    print("   ✓ outputs/scored_candidates.json")

    if generate_report:
        generate_pdf_report(results, jd, report_path)

    # Console summary
    print("\n" + "="*62)
    print("  FINAL RANKINGS")
    print("="*62)
    print(f"  {'#':<3} {'Candidate':<24} {'Sim':<10} {'Score':<8} Decision")
    print(f"  {'-'*58}")
    for r in results:
        print(f"  #{r['rank']:<2} {r['candidate_info']['name']:<24} "
              f"{r['embedding']['similarity_pct']:<10} "
              f"{r['scores']['total_score']:<8.1f} {r['scores']['recommendation']}")

    audit("AGENT_COMPLETE", f"candidates={len(results)}")
    return results
