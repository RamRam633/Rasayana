# Vayu Materia

Knowledge hub for **Indian traditional-medicine formulations** — Ayurveda · Unani ·
Siddha · Sowa Rigpa · Yoga. It ingests open sources, normalizes them into a
**provenance-first Postgres knowledge graph**, and serves it through a FastAPI core
consumed by an **MCP server** (Claude Desktop) and a **Streamlit UI**, with an AI
query layer (**RAG + text-to-SQL**).

> **Status:** runs locally end-to-end. Postgres + pgvector, the FastAPI core,
> the MCP server, and the Streamlit UI are all wired, with a **curated demo
> dataset** (12 plants, 10 phytochemicals, 2 formulations — plants resolved live
> via GBIF, chemicals via PubChem) and a **provider-fallback AI layer**
> (text-to-SQL over Groq/Cerebras/OpenRouter/NVIDIA). Next: the IMPPAT and
> pharmacopoeia extractors (currently honest stubs).

---

## ⚕️ Disclaimer (read first)

This project organizes **traditional and research claims** about plants and
formulations. It is **not medical advice**, not a substitute for a qualified
practitioner, and makes **no safety or efficacy guarantees**. Every served claim is
tagged with its evidence level (`traditional | ethnobotanical | preclinical |
clinical`) and its source. Do not act on it clinically.

---

## Architecture

```
SOURCES ──► EXTRACT (one adapter/source, license-tagged)
                    │
   BRONZE (raw, immutable) ─► SILVER (normalized + entity-resolved) ─► GOLD (serving views)
        data/raw/                 canonical IDs, confidence, provenance      kg views
                    │
                    ▼
        POSTGRES (Supabase) + pgvector          ← single backbone
                    │
        ┌───────────┴─────────────┐
        ▼                         ▼
   FastAPI core  ──────────►  AI query layer
   (vayu/api)                 router → RAG (chunks) | text-to-SQL (read-only)
        │
   ┌────┴─────────────┐
   ▼                  ▼
 MCP server        Streamlit UI
 (Claude Desktop)  (categorized browse + query)
```

## Accuracy & provenance contract

Accuracy is the product. The scaffold enforces it structurally:

1. **Every edge row carries `source_id` + `confidence` + `provenance`.** Claims from
   different sources coexist as separate rows; nothing is silently merged.
2. **Canonical-ID resolution.** Chemicals key on **InChIKey**; plants resolve to a
   **POWO/WFO accepted name**. Unresolved entities are flagged, not force-matched.
3. **Extractors fail loudly.** A stub raises rather than returning fabricated data.
   No source = no row.
4. **License gate.** `source.is_redistributable` controls what the API may serve.
   `NULL`/unknown license is treated as non-redistributable. TKDL is **not** ingested
   (access-restricted to patent offices).
5. **Curation gate.** PDF-extracted pharmacopoeia data lands as `is_curated = false`
   draft until reviewed.

## Sources (phase plan)

| Source | Role | License posture | Phase |
|---|---|---|---|
| **IMPPAT 2.0** | plant↔chemical↔use backbone | academic — verify | 1 |
| **Dr. Duke's** (USDA) | chemical↔bioactivity cross-ref | public domain | 1 |
| **PubChem / ChEBI** | chemical canonical IDs | open | 1 (PubChem ✅ implemented) |
| **POWO / WFO / GBIF** | botanical name resolution | open | 1 |
| **API / AFI / Unani / Siddha Pharmacopoeia** | formulations | govt — verify | 2 (PDF + curation) |
| **ICD-11 (incl. TM2) / MeSH** | indication vocabulary | open | enrichment |
| **TKDL** | — | **closed, not ingested** | — |

Every source is declared in [`config/sources.yaml`](config/sources.yaml) with its
license and `is_redistributable` flag.

## Quickstart (local)

```bash
cp .env.example .env     # then fill in DATABASE_URL + at least one LLM provider key
make setup               # venv (Python 3.11) + install
make db-start            # start local Homebrew Postgres 17 + create the 'vayu' db
make db-schema           # apply schema + views + seeds + read-only role
make seed                # load the curated demo dataset (live GBIF + PubChem)
make api                 # FastAPI core  -> http://localhost:8000  (/docs)
make ui                  # Streamlit UI  -> http://localhost:8501
make mcp                 # MCP server (stdio) for Claude Desktop
make test
```

Everything is env-driven. The DB can be local Postgres (above) or a Supabase
connection string. The AI layer needs **one** OpenAI-compatible provider key
(Groq/Cerebras/OpenRouter/NVIDIA) — it falls back across whichever are set. Drop
in `ANTHROPIC_API_KEY` to prefer Claude. `GET /health` reports configured providers.

## Repo layout

```
vayu-materia/
├── config/         sources.yaml (license registry) · settings.py
├── db/             schema.sql · seed/ · views.sql · roles.sql
├── vayu/
│   ├── models.py   pydantic domain models (mirror the schema)
│   ├── db.py       SQLAlchemy engine/session + pgvector
│   ├── etl/        extract/ (per-source) · transform · load · pipeline
│   ├── normalize.py  botanical · chemical · indication resolvers
│   ├── kg.py       graph query helpers
│   ├── rag.py      chunk · embed · retrieve
│   ├── nlsql.py    text-to-SQL with read-only guardrails
│   └── api/        FastAPI core (entities · search · query)
├── mcp_server/     server.py + Claude Desktop config snippet
├── ui/             Streamlit app
├── tests/
└── data/           raw/ (bronze) · interim/ (silver) · processed/ (gold)  [gitignored]
```

## Design notes

See [`docs/`](docs/) for the entity model and the design decisions (provenance
granularity, entity resolution, controlled vocabularies, text-to-SQL safety).
