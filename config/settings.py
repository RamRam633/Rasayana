"""Central configuration. Env-driven (pydantic-settings) + the source registry.

Run all commands from the repo root so `config` is importable.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://vayu:vayu@localhost:5432/vayu"
    database_url_ro: str | None = None  # read-only role for the text-to-SQL path

    # ── LLM providers (OpenAI-compatible). The chain in vayu/llm.py tries each
    # configured provider in order until one answers — same resilience idea as the
    # Vayu llm-fallback-framework. Add ANTHROPIC and reorder to prefer Claude.
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    cerebras_api_key: str | None = None
    cerebras_model: str = "llama-3.3-70b"
    openrouter_api_key: str | None = None
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct"
    nvidia_api_key: str | None = None
    nvidia_model: str = "meta/llama-3.3-70b-instruct"
    # Native Anthropic (optional; not OpenAI-compatible, used directly if set).
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"

    # Embeddings for RAG (optional; RAG has no corpus until phase-2 monographs).
    voyage_api_key: str | None = None
    embedding_model: str = "voyage-3"
    embedding_dim: int = 1024  # keep in sync with vector(...) in db/schema.sql

    # Wiring
    api_base_url: str = "http://localhost:8000"
    env: str = "local"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def load_sources() -> dict[str, dict[str, Any]]:
    """Source registry keyed by short_code. The license/redistributable flags
    here are the compliance gate — the API must not serve a source whose
    `is_redistributable` is false."""
    with open(ROOT / "config" / "sources.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return {s["short_code"]: s for s in data["sources"]}
