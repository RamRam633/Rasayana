"""Load stage — idempotent upserts into Postgres, with provenance.

Entity upserts dedupe on canonical keys (InChIKey for chemicals, accepted_name
for plants). Records that fail the accuracy bar (no canonical key) are skipped
and counted, never force-inserted as a guess.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.orm import Session

from vayu import db
from vayu.models import ChemicalRecord, PlantRecord


@lru_cache
def _sid(short_code: str) -> str | None:
    return db.source_id(short_code)


def upsert_phytochemical(s: Session, rec: ChemicalRecord, src_id: str | None) -> bool:
    if not rec.inchikey:
        return False  # cannot dedupe without a canonical key
    s.execute(
        text(
            """
            insert into phytochemical
              (preferred_name, inchikey, inchi, smiles, molecular_formula,
               molecular_weight, pubchem_cid, source_id)
            values
              (:preferred_name, :inchikey, :inchi, :smiles, :molecular_formula,
               :molecular_weight, :pubchem_cid, :source_id)
            on conflict (inchikey) do update set
              preferred_name   = coalesce(phytochemical.preferred_name, excluded.preferred_name),
              smiles           = coalesce(phytochemical.smiles, excluded.smiles),
              molecular_formula= coalesce(phytochemical.molecular_formula, excluded.molecular_formula),
              pubchem_cid      = coalesce(phytochemical.pubchem_cid, excluded.pubchem_cid)
            """
        ),
        {**rec.model_dump(exclude={"source_code"}), "source_id": src_id},
    )
    return True


def upsert_plant(s: Session, rec: PlantRecord, src_id: str | None) -> bool:
    if not rec.accepted_name:
        return False  # unresolved; leave for curation rather than insert a raw guess
    s.execute(
        text(
            """
            insert into plant
              (accepted_name, genus, family, powo_id, wfo_id, gbif_id,
               resolution_confidence, source_id)
            values
              (:accepted_name, :genus, :family, :powo_id, :wfo_id, :gbif_id,
               :resolution_confidence, :source_id)
            on conflict (accepted_name, kind) do update set
              family = coalesce(plant.family, excluded.family),
              gbif_id = coalesce(plant.gbif_id, excluded.gbif_id)
            """
        ),
        {
            "accepted_name": rec.accepted_name,
            "genus": rec.genus,
            "family": rec.family,
            "powo_id": rec.powo_id,
            "wfo_id": rec.wfo_id,
            "gbif_id": rec.gbif_id,
            "resolution_confidence": rec.resolution_confidence,
            "source_id": src_id,
        },
    )
    return True


def load_records(records: Iterable) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    with db.session() as s:
        for r in records:
            src_id = _sid(getattr(r, "source_code", None))
            if isinstance(r, ChemicalRecord):
                counts["phytochemical" if upsert_phytochemical(s, r, src_id) else "skipped"] += 1
            elif isinstance(r, PlantRecord):
                counts["plant" if upsert_plant(s, r, src_id) else "skipped"] += 1
            else:
                # Edge loading (plant_phytochemical, plant_use, …) lands with the
                # IMPPAT implementation, where both endpoints are resolvable.
                counts["skipped_edge_todo"] += 1
    return dict(counts)
