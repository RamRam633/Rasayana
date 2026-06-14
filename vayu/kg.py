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


def get_stats() -> dict:
    """Headline graph counts for the hero/landing."""
    return _rows(
        """
        select
          (select count(*) from plant)                  as plants,
          (select count(*) from phytochemical)          as phytochemicals,
          (select count(*) from phytochemical where inchikey is not null) as phytochemicals_keyed,
          (select count(*) from target)                 as targets,
          (select count(*) from therapeutic_use)        as therapeutic_uses,
          (select count(*) from source)                 as sources,
          (select count(*) from plant_phytochemical)
            + (select count(*) from plant_use)
            + (select count(*) from phytochemical_activity)
            + (select count(*) from phytochemical_target) as edges
        """
    )[0]


FEATURED = [
    "Withania somnifera", "Curcuma longa", "Ocimum tenuiflorum", "Zingiber officinale",
    "Azadirachta indica", "Bacopa monnieri", "Tinospora cordifolia", "Panax ginseng",
]


def get_featured() -> list[dict]:
    return _rows(
        """
        select p.id, p.accepted_name, p.family,
               (select count(*) from plant_phytochemical x where x.plant_id = p.id) as chems
        from plant p
        where p.accepted_name = any(:names)
        order by array_position(:names, p.accepted_name)
        """,
        names=FEATURED,
    )


def get_plant_detail(plant_id: str) -> dict | None:
    base = _rows(
        "select id, accepted_name, genus, family, resolution_confidence, is_curated "
        "from plant where id = :id",
        id=plant_id,
    )
    if not base:
        return None
    p = base[0]
    p["names"] = _rows(
        "select name, name_kind::text as name_kind, language_code, transliteration "
        "from plant_name where plant_id = :id order by is_preferred desc, name_kind limit 40",
        id=plant_id,
    )
    p["phytochemicals"] = _rows(
        """
        select ph.id, ph.preferred_name, ph.inchikey, ph.pubchem_cid,
               max(pp.evidence::text) as evidence
        from plant_phytochemical pp
        join phytochemical ph on ph.id = pp.phytochemical_id
        where pp.plant_id = :id
        group by ph.id
        order by (ph.preferred_name is not null and ph.preferred_name !~ '^[A-Z]{14}-') desc,
                 (ph.inchikey is not null) desc, ph.preferred_name
        limit 64
        """,
        id=plant_id,
    )
    p["uses"] = _rows(
        """
        select tu.preferred_label, tu.category::text as category, tu.icd11_code,
               max(pu.evidence::text) as evidence, string_agg(distinct s.short_code, ',') as sources
        from plant_use pu
        join therapeutic_use tu on tu.id = pu.therapeutic_use_id
        join source s on s.id = pu.source_id
        where pu.plant_id = :id
        group by tu.preferred_label, tu.category, tu.icd11_code
        order by (max(pu.evidence::text) = 'traditional') desc, tu.preferred_label limit 48
        """,
        id=plant_id,
    )
    p["targets"] = _rows(
        """
        select t.gene_symbol, t.protein_name,
               count(distinct pt.phytochemical_id) as via_chemicals
        from plant_phytochemical pp
        join phytochemical_target pt on pt.phytochemical_id = pp.phytochemical_id
        join target t on t.id = pt.target_id
        where pp.plant_id = :id
        group by t.id, t.gene_symbol, t.protein_name
        order by via_chemicals desc limit 24
        """,
        id=plant_id,
    )
    counts = _rows(
        """
        select
          (select count(distinct phytochemical_id) from plant_phytochemical where plant_id = :id) as chems,
          (select count(distinct therapeutic_use_id) from plant_use where plant_id = :id) as uses
        """,
        id=plant_id,
    )[0]
    p["chem_count"] = counts["chems"]
    p["use_count"] = counts["uses"]
    p["target_count"] = len(p["targets"])
    return p


def get_chemical(chem_id: str) -> dict | None:
    base = _rows(
        "select id, preferred_name, inchikey, pubchem_cid, chembl_id, smiles, molecular_formula, "
        "molecular_weight from phytochemical where id = :id",
        id=chem_id,
    )
    if not base:
        return None
    c = base[0]
    c["plants"] = _rows(
        "select p.id, p.accepted_name, p.family from plant p "
        "join plant_phytochemical pp on pp.plant_id = p.id where pp.phytochemical_id = :id "
        "group by p.id order by p.accepted_name limit 40",
        id=chem_id,
    )
    c["targets"] = _rows(
        "select t.gene_symbol, t.protein_name, pt.activity_type, pt.activity_value, pt.activity_unit "
        "from phytochemical_target pt join target t on t.id = pt.target_id "
        "where pt.phytochemical_id = :id order by t.gene_symbol limit 40",
        id=chem_id,
    )
    return c


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
