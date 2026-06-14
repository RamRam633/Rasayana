"""CMAUP 2.0 bulk loader — adds canonical chemicals (InChIKey), the mechanistic
target layer, and ICD-11-coded plant-disease links.

CMAUP ingredients carry InChIKey/PubChem/ChEMBL, so chemicals here are keyed on
InChIKey (the canonical key). Targets get their own table. Everything is stamped
source='cmaup'; edges are delete-then-insert per source for idempotency.

Files (data/raw/cmaup/, TSV):
  Plants                              -> plant
  Ingredients_All                     -> phytochemical (InChIKey)
  Targets                             -> target
  Plant_Ingredient_Associations       -> plant_phytochemical
  Ingredient_Target_Associations      -> phytochemical_target (mechanistic)
  Plant_Human_Disease_Associations    -> therapeutic_use (ICD-11) + plant_use
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import psycopg

from config.settings import ROOT, get_settings
from vayu import db

DATA_DIR = ROOT / "data" / "raw" / "cmaup"
P = "CMAUPv2.0_download_"

DDL = [
    """create table if not exists target (
        id uuid primary key default gen_random_uuid(),
        cmaup_id text unique,
        gene_symbol text, protein_name text, uniprot_id text, chembl_id text,
        target_class text, source_id uuid references source(id))""",
    """create table if not exists phytochemical_target (
        id uuid primary key default gen_random_uuid(),
        phytochemical_id uuid not null references phytochemical(id) on delete cascade,
        target_id uuid not null references target(id) on delete cascade,
        activity_type text, activity_value text, activity_unit text,
        source_id uuid not null references source(id), provenance jsonb)""",
    "create index if not exists pt_phyto_idx on phytochemical_target (phytochemical_id)",
    "create index if not exists pt_tgt_idx on phytochemical_target (target_id)",
]


def _dsn() -> str:
    return get_settings().database_url.replace("postgresql+psycopg://", "postgresql://")


def _tsv(name: str, cols: list[str], names: list[str] | None = None) -> pd.DataFrame:
    kwargs: dict = {"sep": "\t", "dtype": str, "na_values": ["NA", "n.a.", "na"]}
    if names is not None:  # headerless file
        kwargs.update(header=None, names=names)
        df = pd.read_csv(DATA_DIR / f"{name}.txt", **kwargs)
    else:
        df = pd.read_csv(DATA_DIR / f"{name}.txt", usecols=cols, **kwargs)
    return df.fillna("").apply(lambda c: c.str.strip())[cols]


def _copy(cur, table: str, df: pd.DataFrame, cols: list[str]) -> None:
    buf = io.StringIO()
    df.to_csv(buf, index=False, header=False)
    buf.seek(0)
    with cur.copy(f"COPY {table} ({', '.join(cols)}) FROM STDIN WITH (FORMAT csv)") as cp:
        cp.write(buf.read())


def run(data_dir: Path = DATA_DIR) -> dict[str, int]:
    counts: dict[str, int] = {}
    with psycopg.connect(_dsn(), autocommit=False) as conn, conn.cursor() as cur:
        for stmt in DDL:
            cur.execute(stmt)
        cur.execute(
            "insert into source (short_code, name, kind, publisher, license, is_redistributable) "
            "values ('cmaup','CMAUP 2.0','database','BIDD Group / NUS','free for academic use', true) "
            "on conflict (short_code) do nothing")
        # chemicals are keyed on InChIKey here; drop the name-unique stopgap so
        # CMAUP names can coexist with Duke's name-keyed chemicals.
        cur.execute("drop index if exists uq_phyto_name")
        cur.execute("create index if not exists idx_phyto_name on phytochemical (lower(preferred_name))")
        conn.commit()
        cur.execute("select id from source where short_code='cmaup'")
        src = cur.fetchone()[0]

        # ---- stage ----
        plants = _tsv(f"{P}Plants", ["Plant_ID", "Plant_Name", "Species_Tax_ID",
                                     "Species_Name", "Genus_Name", "Family_Name"])
        plants["acc"] = plants["Species_Name"].where(plants["Species_Name"] != "", plants["Plant_Name"])
        _stage(cur, "t_pl", plants, {"plant_id": "Plant_ID", "acc": "acc", "genus": "Genus_Name",
                                     "family": "Family_Name", "taxid": "Species_Tax_ID"})

        ing = _tsv(f"{P}Ingredients_All", ["np_id", "pref_name", "chembl_id", "pubchem_cid",
                                           "MW", "InChI", "InChIKey", "SMILES"])
        ing = ing[ing["InChIKey"] != ""]
        _stage(cur, "t_ing", ing, {"np_id": "np_id", "pref_name": "pref_name", "chembl_id": "chembl_id",
                                   "cid": "pubchem_cid", "mw": "MW", "inchi": "InChI",
                                   "inchikey": "InChIKey", "smiles": "SMILES"})

        tgt = _tsv(f"{P}Targets", ["Target_ID", "Gene_Symbol", "Protein_Name", "Uniprot_ID",
                                   "ChEMBL_ID", "Target_Class_Level1"])
        _stage(cur, "t_tgt", tgt, {"tid": "Target_ID", "gene": "Gene_Symbol", "protein": "Protein_Name",
                                   "uniprot": "Uniprot_ID", "chembl": "ChEMBL_ID", "klass": "Target_Class_Level1"})

        pi = _tsv(f"{P}Plant_Ingredient_Associations_allIngredients",
                  ["plant_id", "np_id"], names=["plant_id", "np_id"])
        _stage(cur, "t_pi", pi, {"plant_id": "plant_id", "np_id": "np_id"})

        it = _tsv(f"{P}Ingredient_Target_Associations_ActivityValues_References",
                  ["Ingredient_ID", "Target_ID", "Activity_Type", "Activity_Value", "Activity_Unit"])
        _stage(cur, "t_it", it, {"np_id": "Ingredient_ID", "tid": "Target_ID", "atype": "Activity_Type",
                                 "aval": "Activity_Value", "aunit": "Activity_Unit"})

        dis = _tsv(f"{P}Plant_Human_Disease_Associations",
                   ["Plant_ID", "ICD-11 Code", "Disease"])
        _stage(cur, "t_dis", dis, {"plant_id": "Plant_ID", "icd11": "ICD-11 Code", "disease": "Disease"})

        for t, c in (("t_pl", "plant_id"), ("t_ing", "np_id"), ("t_tgt", "tid"),
                     ("t_pi", "plant_id"), ("t_pi", "np_id"), ("t_it", "np_id"), ("t_dis", "plant_id")):
            cur.execute(f"create index on {t} ({c})")
        cur.execute("create index on t_pl (acc)")

        # ---- entities ----
        cur.execute(
            "insert into plant (accepted_name, genus, family, ncbi_taxid, source_id) "
            "select distinct acc, nullif(genus,''), nullif(family,''), "
            "  case when taxid ~ '^[0-9]+$' then taxid::int end, %s "
            "from t_pl where acc <> '' on conflict (accepted_name, kind) do nothing", (src,))
        counts["plants"] = cur.rowcount

        cur.execute(
            "insert into phytochemical (preferred_name, inchikey, inchi, smiles, molecular_weight, "
            "  pubchem_cid, chembl_id, source_id) "
            "select distinct on (inchikey) nullif(pref_name,''), inchikey, nullif(inchi,''), "
            "  nullif(smiles,''), case when mw ~ '^[0-9.]+$' then mw::real end, "
            "  case when cid ~ '^[0-9]+$' then cid::bigint end, nullif(chembl_id,''), %s "
            "from t_ing where inchikey <> '' "
            "and not exists (select 1 from phytochemical p where p.inchikey = t_ing.inchikey)", (src,))
        counts["phytochemicals"] = cur.rowcount

        cur.execute(
            "insert into target (cmaup_id, gene_symbol, protein_name, uniprot_id, chembl_id, target_class, source_id) "
            "select distinct tid, nullif(gene,''), nullif(protein,''), nullif(uniprot,''), "
            "  nullif(chembl,''), nullif(klass,''), %s from t_tgt where tid <> '' "
            "on conflict (cmaup_id) do nothing", (src,))
        counts["targets"] = cur.rowcount

        cur.execute(
            "insert into therapeutic_use (preferred_label, category, icd11_code, source_id) "
            "select distinct disease, 'disease'::indication_category, nullif(icd11,''), %s "
            "from t_dis where disease <> '' on conflict (preferred_label, category) do nothing", (src,))
        counts["therapeutic_uses"] = cur.rowcount
        conn.commit()

        # ---- edges ----
        cur.execute("delete from plant_phytochemical where source_id = %s", (src,))
        cur.execute(
            "insert into plant_phytochemical (plant_id, phytochemical_id, evidence, source_id, provenance) "
            "select distinct p.id, ph.id, 'preclinical'::evidence_level, %s, '{\"src\":\"cmaup.plant_ingredient\"}'::jsonb "
            "from t_pi i join t_pl pl on pl.plant_id = i.plant_id join plant p on p.accepted_name = pl.acc "
            "join t_ing g on g.np_id = i.np_id join phytochemical ph on ph.inchikey = g.inchikey "
            "on conflict do nothing", (src,))
        counts["plant_chemical_edges"] = cur.rowcount

        cur.execute("delete from phytochemical_target where source_id = %s", (src,))
        cur.execute(
            "insert into phytochemical_target (phytochemical_id, target_id, activity_type, activity_value, activity_unit, source_id, provenance) "
            "select ph.id, tg.id, nullif(it.atype,''), nullif(it.aval,''), nullif(it.aunit,''), %s, '{\"src\":\"cmaup.ingredient_target\"}'::jsonb "
            "from t_it it join t_ing g on g.np_id = it.np_id join phytochemical ph on ph.inchikey = g.inchikey "
            "join target tg on tg.cmaup_id = it.tid", (src,))
        counts["phytochemical_target_edges"] = cur.rowcount

        cur.execute("delete from plant_use where source_id = %s", (src,))
        cur.execute(
            "insert into plant_use (plant_id, therapeutic_use_id, evidence, source_id, provenance) "
            "select distinct p.id, u.id, 'preclinical'::evidence_level, %s, '{\"src\":\"cmaup.disease\"}'::jsonb "
            "from t_dis d join t_pl pl on pl.plant_id = d.plant_id join plant p on p.accepted_name = pl.acc "
            "join therapeutic_use u on u.preferred_label = d.disease and u.category = 'disease' "
            "where d.disease <> '' on conflict do nothing", (src,))
        counts["plant_use_edges"] = cur.rowcount

        conn.commit()
    return counts


def _stage(cur, table: str, df: pd.DataFrame, mapping: dict[str, str]) -> None:
    """Create a TEMP table with the mapping's keys as columns and COPY df into it."""
    cols = list(mapping.keys())
    # preserve rows across the mid-run commits; dropped at session close
    cur.execute(f"create temp table {table} ({', '.join(c + ' text' for c in cols)})")
    _copy(cur, table, df[[mapping[c] for c in cols]], cols)
