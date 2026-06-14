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
        select tu.id, tu.preferred_label, tu.category::text as category, tu.icd11_code,
               max(pu.evidence::text) as evidence, string_agg(distinct s.short_code, ',') as sources
        from plant_use pu
        join therapeutic_use tu on tu.id = pu.therapeutic_use_id
        join source s on s.id = pu.source_id
        where pu.plant_id = :id
        group by tu.id, tu.preferred_label, tu.category, tu.icd11_code
        order by (max(pu.evidence::text) = 'traditional') desc, tu.preferred_label limit 48
        """,
        id=plant_id,
    )
    p["targets"] = _rows(
        """
        select t.id, t.gene_symbol, t.protein_name,
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
    p["related"] = _rows(
        "select p2.id, p2.accepted_name, p2.family, "
        "(select count(*) from plant_phytochemical x where x.plant_id = p2.id) as chems "
        "from plant p2 where p2.family is not null and p2.id <> :id "
        "and p2.family = (select family from plant where id = :id) "
        "order by chems desc limit 6", id=plant_id)
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


# ── library browse + detail (paginated lists) ───────────────────────────────
def _count(sql: str, **p) -> int:
    return _rows(sql, **p)[0]["n"]


def list_conditions(q: str | None = None, traditional: bool = True,
                    page: int = 1, page_size: int = 50) -> dict:
    where = ["1=1"]
    params: dict = {}
    if traditional:
        where.append("pu.evidence in ('traditional','ethnobotanical','clinical')")
    if q:
        where.append("tu.preferred_label ilike :q")
        params["q"] = f"%{q}%"
    w = " and ".join(where)
    items = _rows(
        f"""
        select tu.id, tu.preferred_label, tu.category::text as category, tu.icd11_code,
               count(distinct pu.plant_id) as plants
        from therapeutic_use tu
        join plant_use pu on pu.therapeutic_use_id = tu.id
        where {w}
        group by tu.id
        order by plants desc, tu.preferred_label
        limit :limit offset :offset
        """,
        limit=page_size, offset=(page - 1) * page_size, **params)
    total = _count(
        f"select count(*) as n from (select tu.id from therapeutic_use tu "
        f"join plant_use pu on pu.therapeutic_use_id = tu.id where {w} group by tu.id) z",
        **params)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_condition(use_id: str) -> dict | None:
    base = _rows("select id, preferred_label, category::text as category, icd11_code "
                 "from therapeutic_use where id = :id", id=use_id)
    if not base:
        return None
    c = base[0]
    c["plants"] = _rows(
        """
        select p.id, p.accepted_name, p.family,
               max(pu.evidence::text) as evidence,
               string_agg(distinct s.short_code, ',') as sources
        from plant_use pu join plant p on p.id = pu.plant_id join source s on s.id = pu.source_id
        where pu.therapeutic_use_id = :id
        group by p.id
        order by (max(pu.evidence::text) in ('traditional','ethnobotanical','clinical')) desc, p.accepted_name
        limit 300
        """, id=use_id)
    c["plant_count"] = _count("select count(distinct plant_id) as n from plant_use where therapeutic_use_id = :id", id=use_id)
    return c


def list_families(q: str | None = None, page: int = 1, page_size: int = 60) -> dict:
    params: dict = {}
    wq = ""
    if q:
        wq = "and family ilike :q"
        params["q"] = f"%{q}%"
    items = _rows(
        f"""select family, count(*) as plants from plant where family is not null {wq}
            group by family order by plants desc, family limit :limit offset :offset""",
        limit=page_size, offset=(page - 1) * page_size, **params)
    total = _count(f"select count(distinct family) as n from plant where family is not null {wq}", **params)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_family(name: str, page: int = 1, page_size: int = 60) -> dict:
    items = _rows(
        """select p.id, p.accepted_name, p.family,
              (select count(*) from plant_phytochemical x where x.plant_id = p.id) as chems
           from plant p where p.family = :f order by p.accepted_name limit :limit offset :offset""",
        f=name, limit=page_size, offset=(page - 1) * page_size)
    total = _count("select count(*) as n from plant where family = :f", f=name)
    return {"family": name, "items": items, "total": total, "page": page, "page_size": page_size}


def list_molecules(q: str | None = None, named: bool = True,
                   page: int = 1, page_size: int = 50) -> dict:
    where = ["1=1"]
    params: dict = {}
    if named:
        where.append("preferred_name is not null and preferred_name !~ '^[A-Z]{14}-'")
    if q:
        where.append("preferred_name ilike :q")
        params["q"] = f"%{q}%"
    w = " and ".join(where)
    items = _rows(
        f"""select id, preferred_name, inchikey, pubchem_cid, chembl_id, molecular_formula
            from phytochemical where {w} order by preferred_name limit :limit offset :offset""",
        limit=page_size, offset=(page - 1) * page_size, **params)
    total = _count(f"select count(*) as n from phytochemical where {w}", **params)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def list_targets(q: str | None = None, page: int = 1, page_size: int = 50) -> dict:
    params: dict = {}
    wq = ""
    if q:
        wq = "where t.gene_symbol ilike :q or t.protein_name ilike :q"
        params["q"] = f"%{q}%"
    items = _rows(
        f"""select t.id, t.gene_symbol, t.protein_name, t.uniprot_id, t.target_class,
                  count(distinct pt.phytochemical_id) as chems
            from target t left join phytochemical_target pt on pt.target_id = t.id
            {wq} group by t.id order by chems desc, t.gene_symbol limit :limit offset :offset""",
        limit=page_size, offset=(page - 1) * page_size, **params)
    total = _count(f"select count(*) as n from target t {wq}", **params)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_target(tid: str) -> dict | None:
    base = _rows("select id, gene_symbol, protein_name, uniprot_id, chembl_id, target_class "
                 "from target where id = :id", id=tid)
    if not base:
        return None
    t = base[0]
    t["chemicals"] = _rows(
        """select ph.id, ph.preferred_name, ph.inchikey,
                  pt.activity_type, pt.activity_value, pt.activity_unit
           from phytochemical_target pt join phytochemical ph on ph.id = pt.phytochemical_id
           where pt.target_id = :id order by ph.preferred_name limit 120""", id=tid)
    t["plants"] = _rows(
        """select distinct p.id, p.accepted_name, p.family
           from phytochemical_target pt
           join plant_phytochemical pp on pp.phytochemical_id = pt.phytochemical_id
           join plant p on p.id = pp.plant_id
           where pt.target_id = :id order by p.accepted_name limit 80""", id=tid)
    t["chem_count"] = _count("select count(distinct phytochemical_id) as n from phytochemical_target where target_id = :id", id=tid)
    return t


def list_plants_index(q: str | None = None, family: str | None = None,
                      letter: str | None = None, page: int = 1, page_size: int = 50) -> dict:
    where = ["1=1"]
    params: dict = {}
    if family:
        where.append("p.family = :family"); params["family"] = family
    if letter:
        where.append("p.accepted_name ilike :letter"); params["letter"] = f"{letter}%"
    if q:
        where.append("p.accepted_name ilike :q"); params["q"] = f"%{q}%"
    w = " and ".join(where)
    items = _rows(
        f"""select p.id, p.accepted_name, p.family,
               (select count(*) from plant_phytochemical x where x.plant_id = p.id) as chems
            from plant p where {w} order by p.accepted_name limit :limit offset :offset""",
        limit=page_size, offset=(page - 1) * page_size, **params)
    total = _count(f"select count(*) as n from plant p where {w}", **params)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def search_all(q: str, limit: int = 6) -> dict:
    like = f"%{q}%"
    return {
        "plants": _rows("select id, accepted_name as label, family as sub from plant "
                        "where accepted_name ilike :q order by accepted_name limit :n", q=like, n=limit),
        "molecules": _rows("select id, preferred_name as label, inchikey as sub from phytochemical "
                           "where preferred_name ilike :q and preferred_name !~ '^[A-Z]{14}-' "
                           "order by preferred_name limit :n", q=like, n=limit),
        "conditions": _rows("select id, preferred_label as label, category::text as sub from therapeutic_use "
                            "where preferred_label ilike :q order by preferred_label limit :n", q=like, n=limit),
        "targets": _rows("select id, gene_symbol as label, protein_name as sub from target "
                         "where gene_symbol ilike :q or protein_name ilike :q order by gene_symbol limit :n", q=like, n=4),
    }


def get_references() -> list[dict]:
    return _rows(
        """select s.short_code, s.name, s.url, s.license, s.is_redistributable,
              (select count(*) from plant_phytochemical where source_id = s.id)
            + (select count(*) from plant_use where source_id = s.id)
            + (select count(*) from phytochemical_activity where source_id = s.id)
            + (select count(*) from phytochemical_target where source_id = s.id) as edges
           from source s order by edges desc""")


# ── discovery: common ailments → top traditional condition ──────────────────
COMMON_AILMENTS = [
    ("Fever", "Fever"), ("Cough", "Cough"), ("Diarrhea", "Diarrhoea"),
    ("Dysentery", "Dysentery"), ("Rheumatism", "Rheumatism"), ("Headache", "Headache"),
    ("Wound", "Wounds"), ("Inflammation", "Inflammation"), ("Asthma", "Asthma"),
    ("Jaundice", "Jaundice"), ("Diabetes", "Diabetes"), ("Tonic", "Vitality / tonic"),
]


def get_common_ailments() -> list[dict]:
    out = []
    for term, label in COMMON_AILMENTS:
        r = _rows(
            "select tu.id, tu.preferred_label, count(distinct pu.plant_id) as plants "
            "from therapeutic_use tu join plant_use pu on pu.therapeutic_use_id = tu.id "
            "where pu.evidence in ('traditional','ethnobotanical','clinical') "
            "and tu.preferred_label ilike :t "
            "group by tu.id order by plants desc limit 1", t=f"%{term}%")
        if r:
            out.append({"label": label, "id": r[0]["id"],
                        "matched": r[0]["preferred_label"], "plants": r[0]["plants"]})
    return out


def get_plant_overview(plant_id: str) -> dict:
    from vayu import enrich
    row = _rows("select accepted_name from plant where id = :id", id=plant_id)
    if not row:
        return {"found": False}
    return enrich.wikipedia_summary(row[0]["accepted_name"])
