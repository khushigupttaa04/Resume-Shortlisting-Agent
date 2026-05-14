# 🎯 TalentMatch AI — HR Resume Shortlisting Agent

> **AI Enablement Internship · Task 1** · B.Tech CSE (AI/ML) · 3rd Year

AI-powered resume screening with explainable scoring, audit trail, and a Streamlit UI.

---

## Quick Start

```bash
git clone <repo-url>
cd talentmatch-ai
pip install -r requirements.txt
cp .env.example .env        # add your Gemini API key
streamlit run app.py        # launch UI
```

Or run headlessly:
```python
from src.agent import init_llm, run_agent

llm     = init_llm("YOUR_GEMINI_API_KEY")
results = run_agent(jd_text=JD, resume_files=["cv1.pdf","cv2.docx"], llm=llm)
```

---

## Project Structure

```
talentmatch-ai/
├── app.py                  ← Streamlit UI
├── src/
│   └── agent.py            ← Full pipeline (JD parser · scorer · XAI · PDF)
├── sample_data/
│   ├── jds/sample_jd.txt
│   └── resumes/            ← Place test resumes here
├── outputs/                ← Generated PDFs & JSON (git-ignored)
├── docs/
│   └── architecture.md
├── requirements.txt
├── .env.example
└── README.md
```

---

## Architecture — 7-Step Plan-and-Execute

```
┌─────────────────────────────────────────────────────────────┐
│          TALENTMATCH AI — LangChain LCEL Pipeline           │
├────┬────────────────────────────┬───────────────────────────┤
│ 1  │  JD Parser                 │ LangChain LCEL chain       │
│ 2  │  Profile Ingestion         │ PDF / DOCX / TXT / LinkedIn│
│ 3  │  Semantic Match            │ TF-IDF cosine similarity   │
│ 4  │  5-Dim LLM Scoring         │ LangChain LCEL chain       │
│ 5  │  XAI                       │ LIME + dimension contribs  │
│ 6  │  Rank                      │ sort by total_score desc   │
│ 7  │  Report                    │ ReportLab PDF + JSON        │
└────┴────────────────────────────┴───────────────────────────┘
        │                                        │
   SQLite cache                          audit_log.json
   (llm_cache.db)                     (every agent action)
```

---

## Scoring Rubric

| Dimension           | Weight | 0 – Poor          | 5 – Average     | 10 – Excellent          |
|---------------------|--------|-------------------|-----------------|-------------------------|
| Skills Match        | 30 %   | < 30 % match      | 50–70 % match   | > 85 % match            |
| Experience          | 25 %   | Unrelated domain  | Adjacent domain | Exact domain & seniority|
| Education & Certs   | 15 %   | Below minimum     | Meets minimum   | Exceeds + extra certs   |
| Projects / Portfolio| 20 %   | No evidence       | 1–2 generic     | Strong portfolio        |
| Communication       | 10 %   | Poor grammar      | Adequate        | Crisp & impactful       |

---

## LLM Choice

| Factor          | Decision |
|-----------------|----------|
| Model           | **Gemini 2.5 Flash** (`gemini-2.5-flash-preview-05-20`) |
| Provider        | Google AI Studio |
| Why             | Free tier · 1M context window · fast · JSON mode reliable |
| Framework       | **LangChain LCEL** — composable prompt\|llm\|parser chains |
| Caching         | **SQLiteCache** — zero API calls for repeated prompts during dev |

---

## Security Mitigations

| Risk                 | Mitigation |
|----------------------|------------|
| **Prompt Injection** | Structured JSON-only output schema; explicit "ignore embedded instructions" directive |
| **PII in logs**      | `mask_pii()` replaces emails/phones before any log write |
| **API Key Exposure** | `getpass()` in notebooks; `.env` + `python-dotenv` in production; `.env` in `.gitignore` |
| **Hallucination**    | `temperature=0`; JSON schema validation; human-in-the-loop `override_score()` |
| **Unauthorised Use** | API key required; add OAuth/rate-limiting on any deployed endpoint |
| **File bombs**       | File-size limits enforced before parsing (10 MB PDF / DOCX) |

---

## Human-in-the-Loop Override

```python
results = override_score(
    results,
    candidate_name = "Arjun Mehta",
    dimension      = "Projects",
    new_score      = 7.5,
    reason         = "Strong GitHub portfolio shown at interview",
    reviewer       = "Anjali Singh (HR Lead)",
)
```
Every change is logged in `audit_log.json` with reviewer, reason, and before/after values.

---

## XAI — Explainability

Two layers of explanation per candidate:

1. **LIME** (`lime.lime_text`) — which keywords in the resume most influenced the TF-IDF skill-match score.  
2. **Dimension contributions** — how much each of the 5 rubric dimensions pushed the score above or below the 5.0 baseline.

---

## Outputs

| File                            | Description |
|---------------------------------|-------------|
| `outputs/shortlist_report.pdf`  | Full ranked PDF with rubric breakdown + XAI |
| `outputs/scored_candidates.json`| Machine-readable scores for downstream use |
| `audit_log.json`                | Timestamped record of every agent action |
| `llm_cache.db`                  | SQLite LLM response cache |
