"""Dr. Duke's Phytochemical & Ethnobotanical DB extractor (USDA, public domain).

STUB — cross-reference layer. Implement against the Duke data dump under
data/raw/duke/. Yields, all with source_code='duke':
  * ChemicalRecord          (chemicals, to cross-link by name/InChIKey)
  * phytochemical_activity  (chemical -> biological activity)  [add ActivityEdge]
  * plant_use               (plant -> ethnobotanical use)      [add PlantUseEdge]

Use Duke to corroborate IMPPAT edges (raises confidence) and to add activity
annotations IMPPAT lacks. Reconcile chemicals on InChIKey via PubChem.
"""
from __future__ import annotations

from collections.abc import Iterator

from pydantic import BaseModel

from .base import BaseExtractor


class DukeExtractor(BaseExtractor):
    short_code = "duke"
    phase = 1

    def extract(self, *, name: str | None = None, limit: int | None = None) -> Iterator[BaseModel]:
        raise NotImplementedError(
            "Duke extractor not yet implemented. Place the Duke dump in data/raw/duke/ "
            "and yield ChemicalRecord + activity/use edges (see module docstring)."
        )
        yield  # pragma: no cover
