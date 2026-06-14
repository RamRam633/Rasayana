"""Entity resolution — the accuracy core.

Two working resolvers:
  * ChemicalNormalizer — guarantees an InChIKey (the canonical chemical key).
    Uses the value from the source if present; else derives it from SMILES via
    RDKit (optional [chem] extra). No key and no SMILES => left unresolved.
  * BotanicalResolver — reconciles a raw plant name to an accepted scientific
    name via the GBIF species-match API (open, documented). POWO/WFO can be
    layered on top for accepted-name authority. Low confidence => left flagged,
    never force-matched.

Resolution is NON-DESTRUCTIVE: we attach accepted names + confidence, we never
discard the raw input.
"""
from __future__ import annotations

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from vayu.models import ChemicalRecord, PlantRecord

GBIF_MATCH = "https://api.gbif.org/v1/species/match"
# Below this GBIF confidence (0-100) we treat the plant as unresolved (curate later).
MIN_BOTANICAL_CONFIDENCE = 80


class ChemicalNormalizer:
    def ensure_inchikey(self, rec: ChemicalRecord) -> ChemicalRecord:
        if rec.inchikey:
            return rec
        if rec.smiles:
            ik = _inchikey_from_smiles(rec.smiles)
            if ik:
                return rec.model_copy(update={"inchikey": ik})
        return rec  # unresolved; loader will skip-or-flag


class BotanicalResolver:
    def __init__(self) -> None:
        self._client = httpx.Client(timeout=20.0, headers={"User-Agent": "vayu-materia/0.1"})

    @retry(wait=wait_exponential(multiplier=0.5, max=8), stop=stop_after_attempt(4), reraise=True)
    def _match(self, name: str) -> dict:
        r = self._client.get(GBIF_MATCH, params={"name": name, "kingdom": "Plantae"})
        r.raise_for_status()
        return r.json()

    def resolve(self, rec: PlantRecord) -> PlantRecord:
        m = self._match(rec.raw_name)
        conf = (m.get("confidence") or 0) / 100.0
        if m.get("matchType") == "NONE" or conf < MIN_BOTANICAL_CONFIDENCE / 100.0:
            return rec.model_copy(update={"resolution_confidence": conf})
        return rec.model_copy(
            update={
                "accepted_name": m.get("canonicalName") or rec.raw_name,
                "genus": m.get("genus"),
                "family": m.get("family"),
                "gbif_id": str(m["usageKey"]) if m.get("usageKey") else None,
                "resolution_confidence": conf,
            }
        )


def _inchikey_from_smiles(smiles: str) -> str | None:
    try:
        from rdkit import Chem
        from rdkit.Chem import inchi
    except ImportError:
        return None  # [chem] extra not installed
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return inchi.InchiToInchiKey(inchi.MolToInchi(mol)) or None
