"""Pipeline orchestration — extract -> transform -> load for a named source."""
from __future__ import annotations

from importlib import import_module
from typing import Any

from config.settings import load_sources
from vayu.etl import load, transform

# short_code -> "module:Class"
EXTRACTORS: dict[str, str] = {
    "pubchem": "vayu.etl.extract.pubchem:PubChemExtractor",
    "imppat": "vayu.etl.extract.imppat:ImppatExtractor",
    "duke": "vayu.etl.extract.duke:DukeExtractor",
    "api_ayur": "vayu.etl.extract.pharmacopoeia:PharmacopoeiaExtractor",
}


def _load_extractor(code: str):
    module_path, cls_name = EXTRACTORS[code].split(":")
    return getattr(import_module(module_path), cls_name)()


def list_sources() -> dict[str, dict[str, Any]]:
    registry = load_sources()
    out = {}
    for code, impl in EXTRACTORS.items():
        meta = registry.get(code, {})
        out[code] = {
            "impl": impl,
            "phase": meta.get("phase"),
            "license": meta.get("license"),
            "is_redistributable": meta.get("is_redistributable"),
        }
    return out


def run_ingest(
    source: str, *, name: str | None = None, limit: int | None = None, dry_run: bool = False
) -> dict[str, Any]:
    if source not in EXTRACTORS:
        raise SystemExit(f"unknown source '{source}'. known: {sorted(EXTRACTORS)}")

    extractor = _load_extractor(source)
    raw = list(extractor.extract(name=name, limit=limit))
    normalized = list(transform.normalize(raw))

    summary: dict[str, Any] = {"source": source, "extracted": len(raw), "dry_run": dry_run}
    if dry_run:
        summary["sample"] = [r.model_dump() for r in normalized[:10]]
        return summary

    summary["loaded"] = load.load_records(normalized)
    return summary
