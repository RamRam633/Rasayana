"""Dr. Duke's (CC0) bulk loader — set-based SQL for speed.

Duke already carries clean scientific names + families, so we don't need per-row
GBIF resolution to load it; we COPY the relevant CSV columns into TEMP staging
tables and do set-based INSERT...SELECT into the graph. Everything is stamped
source='duke'; edge tables are delete-then-insert per source for idempotency.

Tables used:
  FNFTAX        -> plant            (FNFNUM, TAXON, GENUS, FAMILY)
  CHEMICALS     -> phytochemical    (CHEM, CASNUM)
  COMMON_NAMES  -> plant_name       (CNNAM, FNFNUM)
  ETHNOBOT      -> therapeutic_use + plant_use   (TAXON, ACTIVITY)
  FARMACY_NEW   -> plant_phytochemical           (FNFNUM, CHEM, PPCO)
  AGGREGAC      -> phytochemical_activity        (CHEM, ACTIVITY)
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import psycopg

from config.settings import ROOT, get_settings
from vayu import db

DATA_DIR = ROOT / "data" / "raw" / "duke" / "csv"


def _dsn() -> str:
    return get_settings().database_url.replace("postgresql+psycopg://", "postgresql://")


def _read(name: str, cols: list[str]) -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / f"{name}.csv", usecols=cols, dtype=str).fillna("")
    for c in cols:
        df[c] = df[c].str.strip()
    return df[cols]


def _copy(cur, table: str, df: pd.DataFrame, cols: list[str]) -> None:
    # df already holds exactly the needed columns in order; COPY maps positionally
    # to the staging column list `cols`.
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False)
    buf.seek(0)
    with cur.copy(f"COPY {table} ({', '.join(cols)}) FROM STDIN WITH (FORMAT csv)") as cp:
        cp.write(buf.read())


def run(data_dir: Path = DATA_DIR) -> dict[str, int]:
    src = db.source_id("duke")
    if not src:
        raise RuntimeError("source 'duke' not seeded — run db/seed/01_reference.sql")

    counts: dict[str, int] = {}
    with psycopg.connect(_dsn(), autocommit=False) as conn, conn.cursor() as cur:
        # functional index on lower(name) for joins + idempotent NOT EXISTS dedupe
        cur.execute(
            "create index if not exists idx_phyto_name on phytochemical (lower(preferred_name))"
        )

        # ---- stage raw CSV columns into TEMP tables ----
        stages = {
            "t_tax": (_read("FNFTAX", ["FNFNUM", "TAXON", "GENUS", "FAMILY"]),
                      ["fnfnum", "taxon", "genus", "family"]),
            "t_chem": (_read("CHEMICALS", ["CHEM", "CASNUM"]), ["chem", "cas"]),
            "t_common": (_read("COMMON_NAMES", ["CNNAM", "FNFNUM"]), ["cname", "fnfnum"]),
            "t_ethno": (_read("ETHNOBOT", ["TAXON", "ACTIVITY"]), ["taxon", "activity"]),
            "t_farmacy": (_read("FARMACY_NEW", ["FNFNUM", "CHEM", "PPCO"]), ["fnfnum", "chem", "part"]),
            "t_agg": (_read("AGGREGAC", ["CHEM", "ACTIVITY"]), ["chem", "activity"]),
        }
        for tbl, (df, cols) in stages.items():
            cur.execute(f"create temp table {tbl} ({', '.join(c + ' text' for c in cols)}) on commit drop")
            _copy(cur, tbl, df, cols)
        cur.execute("create index on t_tax (fnfnum)")
        cur.execute("create index on t_tax (taxon)")

        # ---- entities ----
        cur.execute(
            "insert into plant (accepted_name, genus, family, source_id) "
            "select distinct taxon, nullif(genus,''), nullif(family,''), %s from t_tax where taxon <> '' "
            "on conflict (accepted_name, kind) do nothing", (src,))
        counts["plants"] = cur.rowcount

        cur.execute(
            "insert into phytochemical (preferred_name, source_id) "
            "select distinct c.chem, %s from t_chem c where c.chem <> '' "
            "and not exists (select 1 from phytochemical p where lower(p.preferred_name) = lower(c.chem))",
            (src,))
        counts["phytochemicals"] = cur.rowcount

        cur.execute(
            "insert into therapeutic_use (preferred_label, category, source_id) "
            "select distinct activity, 'disease'::indication_category, %s from t_ethno where activity <> '' "
            "on conflict (preferred_label, category) do nothing", (src,))
        counts["therapeutic_uses"] = cur.rowcount

        # ---- plant vernacular names ----
        cur.execute(
            "insert into plant_name (plant_id, name, name_kind, language_code, source_id) "
            "select distinct p.id, c.cname, 'vernacular'::name_kind, 'eng', %s "
            "from t_common c join t_tax tx on tx.fnfnum = c.fnfnum "
            "join plant p on p.accepted_name = tx.taxon "
            "where c.cname <> '' "
            "and not exists (select 1 from plant_name pn where pn.plant_id = p.id and pn.name = c.cname)",
            (src,))
        counts["plant_names"] = cur.rowcount

        # ---- edges (delete-then-insert per source for idempotency) ----
        cur.execute("delete from plant_phytochemical where source_id = %s", (src,))
        cur.execute(
            "insert into plant_phytochemical (plant_id, phytochemical_id, plant_part, evidence, source_id, provenance) "
            "select distinct p.id, ph.id, nullif(f.part,''), 'preclinical'::evidence_level, %s, '{\"src\":\"duke.farmacy\"}'::jsonb "
            "from t_farmacy f "
            "join t_tax tx on tx.fnfnum = f.fnfnum "
            "join plant p on p.accepted_name = tx.taxon "
            "join phytochemical ph on lower(ph.preferred_name) = lower(f.chem) "
            "where f.chem <> '' on conflict do nothing", (src,))
        counts["plant_chemical_edges"] = cur.rowcount

        cur.execute("delete from plant_use where source_id = %s", (src,))
        cur.execute(
            "insert into plant_use (plant_id, therapeutic_use_id, evidence, source_id, provenance) "
            "select distinct p.id, u.id, 'ethnobotanical'::evidence_level, %s, '{\"src\":\"duke.ethnobot\"}'::jsonb "
            "from t_ethno e "
            "join plant p on p.accepted_name = e.taxon "
            "join therapeutic_use u on u.preferred_label = e.activity and u.category = 'disease' "
            "where e.activity <> '' on conflict do nothing", (src,))
        counts["plant_use_edges"] = cur.rowcount

        cur.execute("delete from phytochemical_activity where source_id = %s", (src,))
        cur.execute(
            "insert into phytochemical_activity (phytochemical_id, activity, evidence, source_id, provenance) "
            "select distinct ph.id, a.activity, 'preclinical'::evidence_level, %s, '{\"src\":\"duke.aggregac\"}'::jsonb "
            "from t_agg a join phytochemical ph on lower(ph.preferred_name) = lower(a.chem) "
            "where a.activity <> ''", (src,))
        counts["phytochemical_activities"] = cur.rowcount

        conn.commit()
    return counts
