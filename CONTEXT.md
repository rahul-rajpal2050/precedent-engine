# Project Context

## Overview
Precedent & Compliance Engine — a Streamlit web app that helps legal/commercial teams review customer contract redlines. It retrieves the closest historical clause from a local vector database (ChromaDB) and uses Claude 3.5 Sonnet to produce a structured JSON verdict covering match category, policy compliance, risk explanation, and a suggested counter-clause.

## Tech Stack
- Python 3.9 (system), venv at `.venv/`
- Streamlit — UI framework
- ChromaDB (persistent, local at `.chroma/`) — vector store for contract clause embeddings
- sentence-transformers (all-MiniLM-L6-v2) — embedding model used by ChromaDB
- Anthropic SDK + claude-3-5-sonnet-20241022 — AI analysis engine
- pypdf, docx2txt — document parsing

## Directory Structure
```
Buildathon/
  app.py              — Streamlit dashboard (sidebar upload + main analysis view)
  config.py           — COMPANY_POLICY static string
  seed_data.py        — One-time script to populate ChromaDB with 3 dummy MSAs
  requirements.txt    — Python dependencies
  core/
    __init__.py
    parser.py         — extract_text() for .txt/.pdf/.docx; chunk_contract() for clause splitting
    database.py       — ChromaDB client; upsert_precedents() and query_clause()
    engine.py         — Anthropic client; analyze_redline() returns structured JSON verdict
  data/               — Placeholder for user-uploaded raw contract files
  .chroma/            — Persistent ChromaDB vector store (auto-created)
  .venv/              — Python virtual environment
```

## Key Files
- `app.py` — entry point; all UI logic; calls core/database.py and core/engine.py
- `core/engine.py` — Claude integration; strict JSON output schema enforced via system prompt
- `core/database.py` — cosine similarity search; converts ChromaDB distances to similarity scores
- `config.py` — company policy injected into every AI prompt
- `seed_data.py` — run once; adds 19 chunks from 3 historical MSAs (ACME, GLOBEX, INITECH)

## Architecture
1. Upload flow (sidebar): file -> parser.extract_text() -> chunk_contract() -> database.upsert_precedents()
2. Analysis flow (main): customer clause -> database.query_clause() -> engine.analyze_redline() -> Streamlit 3-column display
3. Embeddings: SentenceTransformer all-MiniLM-L6-v2 via ChromaDB's built-in embedding function
4. AI call: single Messages API call with structured JSON schema enforced in system prompt; markdown fence stripping on response

## Recent Changes
[2026-06-14] Initial build — all files created, dependencies installed, database seeded with 19 chunks

## Current State
- Fully functional MVP
- ChromaDB seeded with 3 historical MSAs (19 chunks total)
- Requires ANTHROPIC_API_KEY env var to run AI analysis
- .venv created at project root; activate before running
- No test suite yet
