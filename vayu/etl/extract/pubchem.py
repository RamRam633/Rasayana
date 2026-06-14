"""PubChem extractor — the working reference implementation.

Resolves a compound name to canonical chemical identity (CID, InChIKey, formula,
weight) via PUG-REST. This is the spine that gives every phytochemical a stable
key. PUG-REST asks for <= 5 requests/second; we stay well under with backoff.

Note: PubChem has changed the SMILES property name over time, so SMILES is
fetched in a separate, best-effort call and degrades to None rather than failing
the whole record.
"""
from __future__ import annotations

from collections.abc import Iterator
from urllib.parse import quote

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from vayu.models import ChemicalRecord

from .base import BaseExtractor

PUG = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
# Stable property names only (CID is always returned alongside).
CORE_PROPS = "InChIKey,InChI,MolecularFormula,MolecularWeight,IUPACName"


class PubChemExtractor(BaseExtractor):
    short_code = "pubchem"
    phase = 1

    def __init__(self) -> None:
        self._client = httpx.Client(timeout=30.0, headers={"User-Agent": "vayu-materia/0.1"})

    @retry(wait=wait_exponential(multiplier=0.5, max=8), stop=stop_after_attempt(4), reraise=True)
    def _get_json(self, url: str) -> dict | None:
        r = self._client.get(url)
        if r.status_code == 404:
            return None  # compound not found is a legitimate empty result, not an error
        r.raise_for_status()
        return r.json()

    def _smiles(self, name: str) -> str | None:
        for prop in ("SMILES", "CanonicalSMILES", "ConnectivitySMILES"):
            try:
                data = self._get_json(f"{PUG}/compound/name/{quote(name)}/property/{prop}/JSON")
            except httpx.HTTPError:
                continue
            if data:
                props = data.get("PropertyTable", {}).get("Properties", [])
                if props and prop in props[0]:
                    return props[0][prop]
        return None

    def by_name(self, name: str) -> ChemicalRecord | None:
        data = self._get_json(f"{PUG}/compound/name/{quote(name)}/property/{CORE_PROPS}/JSON")
        if not data:
            return None
        props = data["PropertyTable"]["Properties"][0]
        mw = props.get("MolecularWeight")
        return ChemicalRecord(
            preferred_name=props.get("IUPACName") or name,
            inchikey=props.get("InChIKey"),
            inchi=props.get("InChI"),
            smiles=self._smiles(name),
            molecular_formula=props.get("MolecularFormula"),
            molecular_weight=float(mw) if mw not in (None, "") else None,
            pubchem_cid=props.get("CID"),
            source_code=self.short_code,
        )

    def extract(self, *, name: str | None = None, limit: int | None = None) -> Iterator[ChemicalRecord]:
        if not name:
            raise ValueError(
                "PubChem extractor is a single-entity resolver: pass --name <compound>. "
                "Bulk runs feed it the chemical names emitted by the IMPPAT extractor."
            )
        rec = self.by_name(name)
        if rec is not None:
            yield rec
