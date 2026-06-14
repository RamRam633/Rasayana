"""FastAPI core. Single backend; the MCP server and Streamlit UI both call it.

Browse/lookup endpoints need only the DB. /query (text-to-SQL or RAG) also needs
an LLM provider; it returns 503 with a clear message if none is configured, so the
rest of the app stays usable.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config.settings import load_sources
from vayu import __version__, db, kg, llm, nlsql, rag
from vayu.models import AnswerOut, Citation

app = FastAPI(title="Vayu Materia API", version=__version__)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Cues that favor structured aggregation (text-to-SQL) over narrative (RAG).
_SQL_CUES = ("how many", "count", "list", "which", "contain", "ingredient",
             "formulation", "top ", "most", "average", "property", "rasa", "dosha")


def _route(question: str) -> str:
    q = question.lower()
    return "sql" if any(c in q for c in _SQL_CUES) else "rag"


def _citations(short_codes: set[str]) -> list[Citation]:
    reg = load_sources()
    out = []
    for code in sorted(c for c in short_codes if c):
        meta = reg.get(code, {})
        out.append(Citation(source_code=code, name=meta.get("name"),
                            url=meta.get("url"), license=meta.get("license")))
    return out


class QueryIn(BaseModel):
    question: str
    mode: str | None = None  # 'sql' | 'rag' | None (auto-route)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "db": db.healthcheck(),
        "llm_providers": llm.available(),
        "version": __version__,
    }


@app.get("/sources")
def sources() -> list[dict]:
    return list(load_sources().values())


@app.get("/plants")
def plants(q: str = "", limit: int = 20) -> list[dict]:
    return kg.search_plants(q, limit=limit)


@app.get("/plants/{plant_id}")
def plant(plant_id: str) -> dict:
    p = kg.get_plant(plant_id)
    if not p:
        raise HTTPException(404, "plant not found")
    return p


@app.get("/formulations/{formulation_id}")
def formulation(formulation_id: str) -> dict:
    f = kg.get_formulation(formulation_id)
    if not f:
        raise HTTPException(404, "formulation not found")
    return f


@app.get("/phytochemicals/{inchikey}/plants")
def plants_with_chem(inchikey: str, limit: int = 50) -> list[dict]:
    return kg.plants_with_phytochemical(inchikey, limit=limit)


@app.post("/query", response_model=AnswerOut)
def query(payload: QueryIn) -> AnswerOut:
    mode = payload.mode or _route(payload.question)
    try:
        if mode == "sql":
            res = nlsql.ask(payload.question)
            codes = {r.get("source") for r in res["rows"] if isinstance(r, dict)}
            try:
                answer, _ = nlsql.synthesize(payload.question, res["rows"])
            except Exception:  # synthesis is best-effort; rows still returned
                answer = f"{len(res['rows'])} row(s) matched — see the table below."
            return AnswerOut(
                answer=answer, mode="sql", provider=res.get("provider"),
                sql=res["sql"], rows=res["rows"], citations=_citations(codes),
            )
        passages = rag.retrieve(payload.question)
        codes = {p.get("source") for p in passages}
        return AnswerOut(
            answer="Top passages retrieved.", mode="rag",
            passages=passages, citations=_citations(codes),
        )
    except RuntimeError as e:  # no LLM/embeddings configured
        raise HTTPException(503, str(e)) from e
    except ValueError as e:  # guardrail rejected the generated SQL
        raise HTTPException(400, f"query rejected by guardrail: {e}") from e
