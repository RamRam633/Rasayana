"""MCP server for Claude Desktop. Thin tools over the FastAPI core (single
source of truth). Start the API first (`make api`), then point Claude Desktop at
this server (see claude_desktop_config.example.json).

Run: python -m mcp_server.server   (stdio transport)
"""
from __future__ import annotations

import httpx
from mcp.server.fastmcp import FastMCP

from config.settings import get_settings

BASE = get_settings().api_base_url
mcp = FastMCP("vayu-materia")


def _get(path: str, **params) -> object:
    r = httpx.get(f"{BASE}{path}", params=params, timeout=30.0)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def search_plants(query: str, limit: int = 20) -> list[dict]:
    """Search medicinal plants by accepted scientific name or vernacular name."""
    return _get("/plants", q=query, limit=limit)


@mcp.tool()
def get_plant(plant_id: str) -> dict:
    """Get a plant overview (family, Sanskrit name, phytochemical/use counts)."""
    return _get(f"/plants/{plant_id}")


@mcp.tool()
def get_formulation(formulation_id: str) -> dict:
    """Get a formulation with its ingredients and indications."""
    return _get(f"/formulations/{formulation_id}")


@mcp.tool()
def ask_vayu(question: str, mode: str | None = None) -> dict:
    """Ask a natural-language question. Auto-routes to text-to-SQL (structured)
    or RAG (narrative); pass mode='sql' or 'rag' to force one. Returns the answer
    with the backing SQL/passages and source citations."""
    r = httpx.post(f"{BASE}/query", json={"question": question, "mode": mode}, timeout=60.0)
    r.raise_for_status()
    return r.json()


@mcp.tool()
def list_sources() -> list[dict]:
    """List ingested sources with their licenses and redistribution flags."""
    return _get("/sources")


if __name__ == "__main__":
    mcp.run()
