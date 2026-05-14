# HR Resume Shortlisting Agent

AI-powered resume screening and explainable candidate ranking platform built using LangChain LCEL, Gemini, Streamlit, TF-IDF semantic matching, and LIME Explainable AI.

---

# Project Overview

HR Resume Shortlisting Agent automates the first round of resume screening using:

- Semantic skill matching
- Multi-dimensional AI evaluation rubric
- Explainable AI (XAI)
- Human-in-the-loop score override
- Audit logging
- PDF shortlist generation

The platform evaluates candidates against a Job Description (JD) and produces:

- Ranked candidate shortlist
- Dimension-level scoring
- Justifications per score
- XAI insights
- Recruiter override capability
- Downloadable PDF report

The system follows the internship specification and mandatory rubric provided in the enablement brief.

---

# Key Features

## Resume Parsing

Supports:
- PDF
- DOCX
- TXT
- LinkedIn JSON exports

---

## AI-Based Candidate Evaluation

Candidates are scored on:

| Dimension | Weight |
|---|---|
| Skills Match | 30% |
| Experience | 25% |
| Projects | 20% |
| Education & Certifications | 15% |
| Communication | 10% |

The scoring rubric strictly follows the internship requirements.

---

## Semantic Skill Matching

Uses:
- TF-IDF cosine similarity
- Fuzzy matching
- Acronym detection
- Keyword overlap

Improved semantic detection supports:
- NLP ↔ Natural Language Processing
- ML ↔ Machine Learning
- APIs ↔ REST API
- PyTorch ↔ torch

Implemented in:
- `calculate_skill_match()`
- `compute_tfidf_similarity()`

---

# Explainable AI (XAI)

The platform includes multiple explainability layers:

## 1. LIME Keyword Importance

Highlights which resume keywords most influenced the AI score.

## 2. Dimension Contribution Analysis

Shows how each rubric dimension affected the final score relative to baseline.

## 3. Visual XAI Dashboard

Interactive graphs include:
- Candidate comparison charts
- Heatmaps
- Radar plots
- Similarity vs score scatterplots
- Dimension contribution graphs

---

# Human-in-the-Loop (HITL)

Recruiters can manually override any dimension score.

Features:
- Real-time score preview
- Updated weighted total
- Audit logging
- Reason tracking
- Reviewer attribution

Every override is permanently logged to:
- `audit_log.json`
- `audit_log.txt`

---

# Security Mitigations

The project includes mandatory security controls required by the internship brief.

| Risk | Mitigation |
|---|---|
| Prompt Injection | Structured prompts + JSON output parsing |
| API Key Exposure | `.env` + `python-dotenv` + `.gitignore` |
| PII Leakage | Email and phone masking in logs |
| Hallucination | Structured rubric + deterministic temperature |
| Unauthorized Access | Local-only prototype deployment |
| Auditability | Persistent audit logs |
| Resume Privacy | Local processing pipeline |

---

# Technical Stack & Decision Log

## LLM Chosen

### Gemini 2.0 Flash / Gemini 3.1 Flash Lite

Chosen because:
- Fast inference speed
- Low latency
- Good structured JSON generation
- Free-tier friendly
- Strong LangChain support

---

## Agent Framework

### LangChain LCEL

Architecture:
- Sequential Plan-and-Execute pipeline

Pipeline:
1. Parse JD
2. Read resumes
3. Extract candidate profile
4. Compute semantic similarity
5. AI rubric scoring
6. Generate XAI explanations
7. Rank candidates
8. Generate report

---

## Frontend

### Streamlit

Used for:
- Interactive recruiter dashboard
- Resume upload
- Results visualization
- XAI graphs
- Human override controls
- Audit inspection

Custom UI includes:
- Warm beige/pastel yellow design system
- Interactive charts
- Responsive layout
- Multi-tab dashboard

---

## Explainability

### LIME

Used to generate local feature importance explanations for resume scoring.

---

## Semantic Matching

### TF-IDF + Cosine Similarity

Used for semantic similarity between:
- Resume content
- Job Description skills

Implemented using:
- `sklearn`
- `TfidfVectorizer`
- `cosine_similarity`

---

## Caching

### SQLite Cache

Used via LangChain caching to:
- Reduce repeated LLM API calls
- Lower cost
- Improve speed

---

## PDF Reporting

### ReportLab

Used for:
- Professional shortlist reports
- Candidate ranking tables
- XAI explanations
- Audit-ready output

---

## Observability (Bonus)

Prepared for:
- LangSmith
- Langfuse tracing

Mentioned in sidebar stack and architecture for observability bonus marks.

---

# Project Architecture

```text
User Uploads JD + Resumes
            │
            ▼
    Streamlit Frontend
            │
            ▼
      LangChain LCEL
            │
 ┌──────────┼──────────┐
 │          │          │
 ▼          ▼          ▼
JD Parser  Resume Parser  LinkedIn Parser
 │          │
 ▼          ▼
Semantic Matching (TF-IDF)
 │
 ▼
LLM Rubric Scoring
 │
 ▼
LIME Explainability
 │
 ▼
Candidate Ranking
 │
 ▼
PDF Report + Audit Logs
