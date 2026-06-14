"""Database access. Plain SQLAlchemy Core/sessions over the SQL schema — we keep
queries as readable SQL rather than a heavy ORM, which also keeps the schema the
LLM sees (text-to-SQL) identical to the schema we run against.
"""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import get_settings

_engine: Engine | None = None
_Session: sessionmaker | None = None


def engine() -> Engine:
    """Read/write engine (ETL + API)."""
    global _engine, _Session
    if _engine is None:
        s = get_settings()
        _engine = create_engine(
            s.database_url, pool_pre_ping=True, future=True,
            # prepare_threshold=None keeps psycopg3 safe behind a transaction pooler
            # (Neon's pooled endpoint / pgbouncer), which rejects server-side prepares.
            connect_args={"prepare_threshold": None},
        )
        _Session = sessionmaker(bind=_engine, future=True, expire_on_commit=False)
    return _engine


def ro_engine() -> Engine:
    """Read-only engine for the text-to-SQL path (connects as vayu_ro if configured)."""
    s = get_settings()
    url = s.database_url_ro or s.database_url
    return create_engine(
        url, pool_pre_ping=True, future=True,
        connect_args={"prepare_threshold": None},
    )


@contextmanager
def session() -> Iterator[Session]:
    if _Session is None:
        engine()
    assert _Session is not None
    sess = _Session()
    try:
        yield sess
        sess.commit()
    except Exception:
        sess.rollback()
        raise
    finally:
        sess.close()


def healthcheck() -> bool:
    try:
        with engine().connect() as c:
            return c.execute(text("select 1")).scalar() == 1
    except Exception:
        return False


def source_id(short_code: str) -> str | None:
    """Resolve a source short_code to its UUID (for provenance on every edge)."""
    with engine().connect() as c:
        return c.execute(
            text("select id from source where short_code = :c"), {"c": short_code}
        ).scalar()


# Knowledge tables (truncated by reset_knowledge); reference tables are preserved.
KNOWLEDGE_TABLES = [
    "chunk", "document", "xref", "entity_property", "phytochemical_activity",
    "formulation_use", "formulation_ingredient", "plant_use", "plant_phytochemical",
    "formulation", "therapeutic_use", "phytochemical", "plant_name", "plant",
]


def reset_knowledge() -> None:
    """Truncate all knowledge tables (retain source/system/language/property_term).
    Used to retire the demo seed before bulk ingest."""
    existing = {"plant", "plant_name", "phytochemical", "therapeutic_use", "formulation",
                "plant_phytochemical", "plant_use", "formulation_ingredient",
                "formulation_use", "phytochemical_activity", "entity_property", "xref",
                "document", "chunk"}
    with engine().begin() as c:
        # include optional mechanistic tables if they exist
        for opt in ("phytochemical_target", "target", "pathway"):
            if c.execute(text("select to_regclass(:t)"), {"t": opt}).scalar():
                existing.add(opt)
        c.execute(text("truncate " + ", ".join(existing) + " restart identity cascade"))
