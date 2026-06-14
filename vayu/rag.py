"""RAG layer — chunk, embed (Voyage), and retrieve (pgvector cosine).

Narrative text (pharmacopoeia monographs, descriptions) lives in `document`,
split into `chunk` rows with embeddings. Retrieval is semantic + optional
entity filter. Embeddings need VOYAGE_API_KEY and the [ai] extra.
"""
from __future__ import annotations

from sqlalchemy import text

from config.settings import get_settings
from vayu import db


def chunk_text(body: str, target_chars: int = 1200, overlap: int = 150) -> list[str]:
    """Paragraph-greedy splitter with small overlap. Good enough for monographs;
    swap for a token-aware splitter when you tune retrieval."""
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) + 2 <= target_chars:
            buf = f"{buf}\n\n{p}" if buf else p
        else:
            if buf:
                chunks.append(buf)
            buf = (buf[-overlap:] + "\n\n" + p) if buf else p
    if buf:
        chunks.append(buf)
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    s = get_settings()
    if not s.voyage_api_key:
        raise RuntimeError("VOYAGE_API_KEY not set — cannot embed. (pip install '.[ai]')")
    import voyageai  # lazy

    client = voyageai.Client(api_key=s.voyage_api_key)
    result = client.embed(texts, model=s.embedding_model, input_type="document")
    return result.embeddings


def retrieve(query: str, k: int = 6, entity_type: str | None = None) -> list[dict]:
    """Embed the query and return the k nearest chunks (cosine), with provenance."""
    qvec = embed_texts([query])[0]
    vec_literal = "[" + ",".join(f"{x:.7f}" for x in qvec) + "]"  # numeric-only, safe
    filter_sql = "and d.entity_type = :etype" if entity_type else ""
    with db.engine().connect() as c:
        rows = c.execute(
            text(
                f"""
                select ch.text, d.title, d.url, s.short_code as source,
                       1 - (ch.embedding <=> :v::vector) as score
                from chunk ch
                join document d on d.id = ch.document_id
                left join source s on s.id = d.source_id
                where ch.embedding is not null {filter_sql}
                order by ch.embedding <=> :v::vector
                limit :k
                """
            ),
            {"v": vec_literal, "k": k, "etype": entity_type},
        ).mappings().all()
    return [dict(r) for r in rows]
