# ERLA — Epistemic Research Landscape Agent

ERLA is a recursive research navigator for scientific literature. It searches academic paper sources, follows citation/reference structure, summarizes papers, validates generated text against source material, and grows a branching research map through autonomous Scouts.

The immediate product direction is not to become a generic AI writing assistant. ERLA should become a research mission-control dashboard: a system that helps researchers understand a field, inspect evidence, identify gaps and contradictions, and decide what to read or investigate next.

## Current repository state

This repository currently contains a Python-first research core and CLI prototype.

Implemented or partially implemented:

- Paper search through Semantic Scholar.
- Paper search through arXiv.
- Composite multi-provider search with parallel/fallback/single strategies.
- PDF text extraction through PyMuPDF.
- LLM summarization through OpenRouter-compatible APIs.
- Local and HTTP HaluGate validation.
- Recursive research orchestration with Inner Loop, Iteration Loop, Branch Manager, Master Agent, Managing Agent, Reflection Agent, and Hypothesis generation.
- Convex event emission client for realtime visualization.
- Typer CLI commands for search, fetch, and profile listing.

Not yet production-ready:

- No full web dashboard.
- No durable product database.
- No user/project/session API.
- No job queue for long research runs.
- No claim-level evidence ledger.
- No source-of-truth frontend architecture.
- The CLI is still the primary interface.

## Product thesis

ERLA should help a researcher move from an unclear research question to:

1. A mapped research landscape.
2. A live Scout/branch tree.
3. A paper library.
4. Validated paper summaries.
5. Atomic claims linked to evidence.
6. Gap and contradiction analysis.
7. A reading plan.
8. Evidence-backed research-direction recommendations.
9. Exportable notes, citations, and review outlines.

## Architecture summary

Current package layout:

```txt
src/
  cli.py                         Typer CLI entrypoint
  summarize.py                   LLM paper summarization
  config/                        Pydantic config and model profiles
  semantic_scholar/              Semantic Scholar client, models, protocols, adapter
  arxiv/                         arXiv client and adapter
  paper_sources/                 composite provider and deduplication
  halugate/                      local + HTTP hallucination validation
  orchestration/                 recursive research loops and agents
  hypothesis/                    hypothesis generation and validation
  context/                       context estimation and branch splitting
  llm/                           OpenRouter adapter and LLM protocols
  storage/                       Convex realtime event client
```

Target product architecture:

```txt
apps/web/                        Next.js dashboard
apps/api/                        FastAPI product API
src/                             existing research core, migrated carefully
workers/                         background jobs
migrations/                      database migrations
docs or root *.md                source-of-truth product/engineering docs
```

The existing `src` package should be preserved as the research core for now. Do not rewrite it wholesale before the dashboard, API, durable state, and validation model are defined.

## Installation

Python requirement is currently 3.13 or newer.

Recommended development setup:

```bash
uv sync
```

Alternative:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Environment variables

Create a local `.env` file. Do not commit secrets.

Required for real LLM runs:

```bash
OPENROUTER_API_KEY=...
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=anthropic/claude-3-5-sonnet
```

Optional:

```bash
MODEL_PROFILE=research-fast
SEMANTIC_SCHOLAR_API_KEY=...
HALUGATE_URL=http://localhost:8000
HALUGATE_DEVICE=cpu
HALUGATE_USE_SENTINEL=true
CONVEX_URL=...
```

## CLI usage

The CLI is a developer/prototype interface, not the final product UX.

List config profiles:

```bash
erla profiles
```

Search Semantic Scholar:

```bash
erla search "wave optics gravitational wave lensing" --source semantic_scholar --limit 10
```

Search arXiv:

```bash
erla search "transformer attention" --source arxiv --arxiv-cat cs.LG --limit 10
```

Search multiple providers:

```bash
erla search "LLM reasoning" --source semantic_scholar --source arxiv --strategy parallel --limit 20
```

Fetch paper metadata:

```bash
erla fetch arxiv:2301.00001
```

Fetch with PDF text extraction when available:

```bash
erla fetch arxiv:2301.00001 --with-text
```

## HaluGate service

Run validation service locally:

```bash
HALUGATE_DEVICE=cpu uvicorn src.halugate.server:app --host 0.0.0.0 --port 8000
```

The HaluGate service exposes:

- `GET /health`
- `POST /validate`

For production, move heavy validation to a separately deployed service with batching, caching, timeouts, and GPU support where appropriate.

## Development direction

The next engineering milestone is a web dashboard MVP:

1. Add FastAPI product API under `apps/api` or `src/api`.
2. Add durable Postgres schema.
3. Add background worker queue.
4. Add Next.js dashboard under `apps/web`.
5. Connect session creation to the existing `ResearchSession` / `MasterAgent` orchestration.
6. Stream events to the dashboard.
7. Add branch tree, paper inspector, and event log.
8. Add claim extraction and claim evidence ledger.

## Source-of-truth docs

Read these files before making product or architecture changes:

- `PRODUCT_SPEC.md`
- `ARCHITECTURE.md`
- `DATA_MODEL.md`
- `VALIDATION_RULES.md`
- `AGENT_RULES.md`
- `UI_UX_SPEC.md`
- `ROADMAP.md`
- `CODEX.md`
- `TESTING_STRATEGY.md`
- `CODE_STYLE.md`

## Non-goals for the next milestone

Do not prioritize:

- A full AI writing editor.
- Payment system.
- Browser extension.
- Mobile app.
- Enterprise admin dashboard.
- Fancy 3D visualization before usable graph navigation.
- Major refactors that do not unblock the dashboard or validation layer.

## Core rule

If ERLA produces a factual claim, that claim must eventually be decomposed, validated, and linked to source evidence. Unsupported or speculative output must be labeled as such.
