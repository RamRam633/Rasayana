"""Transform stage — apply entity resolution to a stream of extracted records.

Dispatches by record type so a single ingest run can interleave plants and
chemicals. Resolution detail lives in vayu.normalize.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator

from pydantic import BaseModel

from vayu.models import ChemicalRecord, PlantRecord
from vayu.normalize import BotanicalResolver, ChemicalNormalizer


def normalize(records: Iterable[BaseModel]) -> Iterator[BaseModel]:
    chem = ChemicalNormalizer()
    bot = BotanicalResolver()
    for r in records:
        if isinstance(r, ChemicalRecord):
            yield chem.ensure_inchikey(r)
        elif isinstance(r, PlantRecord):
            yield bot.resolve(r)
        else:
            yield r  # edges and other records pass through to the loader
