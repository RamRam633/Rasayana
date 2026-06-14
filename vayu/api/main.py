"""FastAPI core. Single backend; the MCP server and Streamlit UI both call it.

Browse/lookup endpoints need only the DB. /query (text-to-SQL or RAG) also needs
an LLM provider; it returns 503 with a clear message if none is configured, so the
rest of the app stays usable.
"""
from __future__ import annotations

import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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


@app.get("/stats")
def stats() -> dict:
    return kg.get_stats()


@app.get("/featured")
def featured() -> list[dict]:
    return kg.get_featured()


@app.get("/plants/{plant_id}/detail")
def plant_detail(plant_id: str) -> dict:
    d = kg.get_plant_detail(plant_id)
    if not d:
        raise HTTPException(404, "plant not found")
    return d


@app.get("/chemicals/{chem_id}")
def chemical(chem_id: str) -> dict:
    c = kg.get_chemical(chem_id)
    if not c:
        raise HTTPException(404, "phytochemical not found")
    return c


# ── library browse ──────────────────────────────────────────────────────────
@app.get("/conditions")
def conditions(q: str | None = None, traditional: bool = True, page: int = 1, page_size: int = 50) -> dict:
    return kg.list_conditions(q=q, traditional=traditional, page=page, page_size=page_size)


@app.get("/conditions/{use_id}")
def condition(use_id: str) -> dict:
    c = kg.get_condition(use_id)
    if not c:
        raise HTTPException(404, "condition not found")
    return c


@app.get("/families")
def families(q: str | None = None, page: int = 1, page_size: int = 60) -> dict:
    return kg.list_families(q=q, page=page, page_size=page_size)


@app.get("/families/{name}")
def family(name: str, page: int = 1, page_size: int = 60) -> dict:
    return kg.get_family(name, page=page, page_size=page_size)


@app.get("/molecules")
def molecules(q: str | None = None, named: bool = True, page: int = 1, page_size: int = 50) -> dict:
    return kg.list_molecules(q=q, named=named, page=page, page_size=page_size)


@app.get("/targets")
def targets(q: str | None = None, page: int = 1, page_size: int = 50) -> dict:
    return kg.list_targets(q=q, page=page, page_size=page_size)


@app.get("/targets/{tid}")
def target(tid: str) -> dict:
    t = kg.get_target(tid)
    if not t:
        raise HTTPException(404, "target not found")
    return t


@app.get("/plant-index")
def plant_index(q: str | None = None, family: str | None = None, letter: str | None = None,
                page: int = 1, page_size: int = 50) -> dict:
    return kg.list_plants_index(q=q, family=family, letter=letter, page=page, page_size=page_size)


@app.get("/search-all")
def search_all_ep(q: str) -> dict:
    return kg.search_all(q)


@app.get("/references")
def references() -> list[dict]:
    return kg.get_references()


@app.get("/common-ailments")
def common_ailments() -> list[dict]:
    return kg.get_common_ailments()


@app.get("/plants/{plant_id}/overview")
def plant_overview(plant_id: str) -> dict:
    return kg.get_plant_overview(plant_id)


_CHAT_SYS = (
    "You are Rasayana, a precise assistant for an Indian traditional-medicine knowledge "
    "graph (plants, phytochemicals, protein targets, therapeutic uses across Ayurveda, "
    "Unani, Siddha, Sowa Rigpa). Answer ONLY from the provided result rows; never invent "
    "facts. Be concise and clear (2-5 sentences or a short list). Use plain language, and "
    "write with commas, colons, and periods rather than dashes. This is traditional and "
    "research information, not medical advice: give no dosing or treatment instructions. "
    "If rows are empty, say no matching records were found and suggest a rephrase. Mention "
    "source codes (duke/cmaup) when relevant."
)


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj, default=str)}\n\n"


@app.post("/chat")
def chat(payload: QueryIn):
    """Streaming assistant: text-to-SQL over the graph, then a streamed cited answer.
    SSE event shape mirrors the Vayu Tutor: meta / sql / delta / done / error."""
    def gen():
        try:
            res = nlsql.ask(payload.question)
        except ValueError as e:
            yield _sse({"type": "error", "message": f"I couldn't form a safe query: {e}"})
            return
        except Exception as e:  # noqa: BLE001
            yield _sse({"type": "error", "message": f"The query engine is unavailable: {e}"})
            return
        yield _sse({"type": "sql", "sql": res["sql"], "rows": res["rows"][:50],
                    "row_count": len(res["rows"])})
        user = (f"Question: {payload.question}\n\n"
                f"Result rows (JSON):\n{json.dumps(res['rows'][:40], default=str)}")
        try:
            for kind, val in llm.stream(_CHAT_SYS, user):
                yield _sse({"type": "meta", "provider": val} if kind == "meta"
                           else {"type": "delta", "text": val})
            yield _sse({"type": "done"})
        except Exception as e:  # noqa: BLE001
            yield _sse({"type": "error", "message": f"Answer synthesis failed: {e}"})

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


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
                answer = f"{len(res['rows'])} row(s) matched: see the table below."
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
