"""IMPPAT 2.0 extractor — the plant<->chemical<->use backbone.

STUB — implement against the IMPPAT bulk download placed under data/raw/imppat/.
Expected, at minimum:
  * plant master:           IMPPAT id, botanical name, family
  * phytochemical assoc:    IMPPAT plant id, chemical (name + InChIKey), plant part
  * therapeutic-use assoc:  IMPPAT plant id, use term

Yield, all with source_code='imppat':
  * PlantRecord            (raw botanical name -> resolved later by BotanicalResolver)
  * ChemicalRecord         (InChIKey if present; PubChem fills gaps by name)
  * PlantChemicalEdge      (plant_raw_name + chemical key + plant_part)
  * plant_use edges        (see models; add a PlantUseEdge when you wire uses)

Do NOT invent rows for entities absent from the download. Leave unknown fields
None; the loader records confidence and the curation gate handles the rest.
"""
from __future__ import annotations

from collections.abc import Iterator

from pydantic import BaseModel

from .base import BaseExtractor


class ImppatExtractor(BaseExtractor):
    short_code = "imppat"
    phase = 1

    def extract(self, *, name: str | None = None, limit: int | None = None) -> Iterator[BaseModel]:
        raise NotImplementedError(
            "IMPPAT extractor not yet implemented. Download IMPPAT 2.0 to "
            "data/raw/imppat/ and parse it here (see module docstring for the contract). "
            "Verify the IMPPAT license before enabling redistribution in config/sources.yaml."
        )
        yield  # pragma: no cover  (keeps this a generator)
