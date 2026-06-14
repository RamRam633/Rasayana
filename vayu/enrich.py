"""Living enrichment from open sources. Wikipedia plant summaries (CC BY-SA),
fetched on demand and cached — so each plant page can explain itself."""
from __future__ import annotations

import logging
from functools import lru_cache
from urllib.parse import quote

import httpx

log = logging.getLogger("vayu.enrich")
_WIKI = "https://en.wikipedia.org/api/rest_v1/page/summary/"


@lru_cache(maxsize=4096)
def wikipedia_summary(name: str) -> dict:
    """Return {found, title, extract, thumbnail, url} for a species name."""
    try:
        r = httpx.get(_WIKI + quote(name.replace(" ", "_")), timeout=8.0,
                      follow_redirects=True, headers={"User-Agent": "vayu-materia/0.1 (research)"})
        if r.status_code != 200:
            return {"found": False}
        d = r.json()
        if d.get("type") == "disambiguation" or not d.get("extract"):
            return {"found": False}
        return {
            "found": True,
            "title": d.get("title"),
            "extract": d.get("extract"),
            "thumbnail": (d.get("thumbnail") or {}).get("source"),
            "url": ((d.get("content_urls") or {}).get("desktop") or {}).get("page"),
        }
    except Exception as e:  # noqa: BLE001
        log.warning("wikipedia fetch failed for %r: %s", name, e)
        return {"found": False}
