"""Import-level + pure-logic smoke tests (no DB, no API keys required)."""
from config.settings import load_sources
from vayu.api.main import _route
from vayu.rag import chunk_text


def test_source_registry_invariants():
    reg = load_sources()
    # Backbone source present; TKDL must never be ingested.
    assert "imppat" in reg
    assert "tkdl" not in reg
    # Public-domain sources flagged redistributable; academic/unknown ones not.
    assert reg["pubchem"]["is_redistributable"] is True
    assert reg["imppat"]["is_redistributable"] is False


def test_query_router():
    assert _route("How many formulations contain ginger?") == "sql"
    assert _route("Tell me about the traditional uses of ashwagandha") == "rag"


def test_chunker_splits_and_returns_nonempty():
    body = "\n\n".join(f"paragraph {i} " + "x" * 400 for i in range(5))
    chunks = chunk_text(body, target_chars=500)
    assert len(chunks) >= 2
    assert all(c.strip() for c in chunks)
