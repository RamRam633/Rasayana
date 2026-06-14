"""Knowledge-graph read helpers. Plain SQL over the GOLD views, returned as dicts.

These back the FastAPI routes and the MCP tools. Traversal across the graph
(plant -> phytochemical -> activity, etc.) is expressed as SQL joins / CTEs —
the Postgres-relational trade-off we chose over a native graph DB.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import text

from vayu import db


def _rows(sql: str, **params: Any) -> list[dict]:
    with db.engine().connect() as c:
        return [dict(r) for r in c.execute(text(sql), params).mappings().all()]


def search_plants(q: str, limit: int = 20) -> list[dict]:
    return _rows(
        """
        select id, accepted_name, family, also_known_as
        from v_plant_search
        where accepted_name ilike :like
           or exists (select 1 from unnest(also_known_as) a where a ilike :like)
        order by similarity(accepted_name, :q) desc
        limit :limit
        """,
        like=f"%{q}%",
        q=q,
        limit=limit,
    )


def get_plant(plant_id: str) -> dict | None:
    rows = _rows("select * from v_plant_overview where id = :id", id=plant_id)
    return rows[0] if rows else None


def get_formulation(formulation_id: str) -> dict | None:
    rows = _rows("select * from v_formulation_detail where id = :id", id=formulation_id)
    return rows[0] if rows else None


def plants_with_phytochemical(inchikey: str, limit: int = 50) -> list[dict]:
    """Example graph traversal: which plants contain a given chemical, and with
    what evidence/source — provenance carried through the join."""
    return _rows(
        """
        select p.id, p.accepted_name, ppc.plant_part, ppc.evidence,
               s.short_code as source
        from phytochemical c
        join plant_phytochemical ppc on ppc.phytochemical_id = c.id
        join plant p on p.id = ppc.plant_id
        join source s on s.id = ppc.source_id
        where c.inchikey = :ik
        order by p.accepted_name
        limit :limit
        """,
        ik=inchikey,
        limit=limit,
    )
