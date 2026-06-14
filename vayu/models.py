"""Pydantic domain models.

Two flavors:
  * `*Out` models — API/UI response shapes (projections of the GOLD views).
  * `*Record` models — normalized records an extractor yields BEFORE load.
    Every Record carries `source_code` so provenance is never optional.
"""
from __future__ import annotations

from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class EvidenceLevel(str, Enum):
    traditional = "traditional"
    ethnobotanical = "ethnobotanical"
    preclinical = "preclinical"
    clinical = "clinical"
    unknown = "unknown"


# ── API output models ────────────────────────────────────────────────────────
class PlantOut(BaseModel):
    id: UUID
    accepted_name: str
    family: str | None = None
    sanskrit_name: str | None = None
    phytochemical_count: int = 0
    use_count: int = 0


class PhytochemicalOut(BaseModel):
    id: UUID
    preferred_name: str | None = None
    inchikey: str | None = None
    pubchem_cid: int | None = None
    molecular_formula: str | None = None


class FormulationOut(BaseModel):
    id: UUID
    name: str
    system_code: str | None = None
    dosage_form: str | None = None
    is_curated: bool = False
    ingredients: list[dict] = []
    indications: list[str] = []


class Citation(BaseModel):
    source_code: str
    name: str | None = None
    url: str | None = None
    license: str | None = None


class AnswerOut(BaseModel):
    """Uniform AI-layer answer: text + the SQL/passages that backed it + citations."""
    answer: str
    mode: str  # 'sql' | 'rag'
    provider: str | None = None  # which LLM provider answered
    sql: str | None = None
    rows: list[dict] | None = None
    passages: list[dict] | None = None
    citations: list[Citation] = []
    disclaimer: str = (
        "Traditional/research information, not medical advice. "
        "Verify with a qualified practitioner."
    )


# ── ETL record models (pre-load, normalized) ────────────────────────────────
class PlantRecord(BaseModel):
    raw_name: str
    accepted_name: str | None = None
    genus: str | None = None
    family: str | None = None
    powo_id: str | None = None
    wfo_id: str | None = None
    resolution_confidence: float | None = None
    source_code: str


class ChemicalRecord(BaseModel):
    preferred_name: str | None = None
    inchikey: str | None = None
    inchi: str | None = None
    smiles: str | None = None
    molecular_formula: str | None = None
    molecular_weight: float | None = None
    pubchem_cid: int | None = None
    source_code: str


class PlantChemicalEdge(BaseModel):
    plant_raw_name: str
    chemical_inchikey: str | None = None
    chemical_name: str | None = None
    plant_part: str | None = None
    evidence: EvidenceLevel = EvidenceLevel.unknown
    confidence: float | None = None
    source_code: str
