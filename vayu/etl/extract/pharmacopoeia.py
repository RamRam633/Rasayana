"""Pharmacopoeia / formulary extractor (phase 2) — formulations from PDFs.

STUB — the hard, accuracy-critical path. Covers the Ayurvedic Pharmacopoeia /
Ayurvedic Formulary of India (and later Unani/Siddha). Source PDFs go under
data/raw/pharmacopoeia/.

Pipeline intent (install the [pdf] extra: pdfplumber):
  1. Extract monograph text per formulation (name, dosage form, classical ref,
     ingredient list with parts + quantities, preparation method, indications).
  2. Yield Formulation + FormulationIngredient + FormulationUse records with
     source_code='api_ayur' and is_curated=False (draft).
  3. Also emit `document`/`chunk` rows of the narrative text for the RAG layer.

CRITICAL: PDF table extraction is error-prone. Everything lands as DRAFT
(is_curated=False) and must pass human review before it is served as curated.
Keep the raw ingredient string in `ingredient_text` even after resolving a plant,
so a reviewer can always check the extraction against the source.
"""
from __future__ import annotations

from collections.abc import Iterator

from pydantic import BaseModel

from .base import BaseExtractor


class PharmacopoeiaExtractor(BaseExtractor):
    short_code = "api_ayur"
    phase = 2

    def extract(self, *, name: str | None = None, limit: int | None = None) -> Iterator[BaseModel]:
        raise NotImplementedError(
            "Pharmacopoeia extractor is phase 2. Install the [pdf] extra, place source "
            "PDFs in data/raw/pharmacopoeia/, and implement monograph parsing per the "
            "module docstring. Verify redistribution terms before serving content."
        )
        yield  # pragma: no cover
