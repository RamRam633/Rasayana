"""Extractor contract.

ACCURACY CONTRACT (every extractor must honor this):
  1. Never fabricate. If a source file/endpoint is missing, raise — do not
     synthesize plausible-looking rows.
  2. Stamp provenance. Every yielded Record sets `source_code = self.short_code`.
  3. Prefer None over a guess. Unknown field -> None, so downstream confidence
     and curation can reason about gaps honestly.
  4. Normalize identity downstream, not here. Extractors emit raw-ish records;
     canonicalization (InChIKey, accepted botanical name) happens in transform.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from pydantic import BaseModel


class BaseExtractor(ABC):
    short_code: str          # must match a config/sources.yaml entry
    phase: int | str = 1

    @abstractmethod
    def extract(self, *, name: str | None = None, limit: int | None = None) -> Iterator[BaseModel]:
        """Yield normalized *Record models (see vayu.models)."""
        raise NotImplementedError
