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
