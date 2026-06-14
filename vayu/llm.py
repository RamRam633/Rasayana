"""LLM access via an OpenAI-compatible provider fallback chain.

We hold free keys for several OpenAI-compatible providers (Groq, Cerebras,
OpenRouter, NVIDIA). `complete()` tries each *configured* provider in order and
returns the first success — the same resilience pattern as the Vayu
llm-fallback-framework. To prefer Claude, set ANTHROPIC_API_KEY and add a native
branch, or use an OpenRouter Claude model.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass

from config.settings import get_settings

log = logging.getLogger("vayu.llm")


@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    api_key: str | None
    model: str


def _chain() -> list[Provider]:
    s = get_settings()
    candidates = [
        Provider("groq", "https://api.groq.com/openai/v1", s.groq_api_key, s.groq_model),
        Provider("cerebras", "https://api.cerebras.ai/v1", s.cerebras_api_key, s.cerebras_model),
        Provider("openrouter", "https://openrouter.ai/api/v1", s.openrouter_api_key, s.openrouter_model),
        Provider("nvidia", "https://integrate.api.nvidia.com/v1", s.nvidia_api_key, s.nvidia_model),
    ]
    return [p for p in candidates if p.api_key]


def available() -> list[str]:
    """Names of configured providers, in fallback order."""
    return [p.name for p in _chain()]


def complete(system: str, user: str, *, max_tokens: int = 800, temperature: float = 0.0) -> tuple[str, str]:
    """Return (text, provider_name). Raises if no provider is configured/working."""
    from openai import OpenAI  # lazy

    chain = _chain()
    if not chain:
        raise RuntimeError(
            "No LLM provider configured. Set one of GROQ_API_KEY / CEREBRAS_API_KEY / "
            "OPENROUTER_API_KEY / NVIDIA_API_KEY in .env."
        )
    errors: list[str] = []
    for p in chain:
        try:
            client = OpenAI(base_url=p.base_url, api_key=p.api_key, timeout=60.0)
            resp = client.chat.completions.create(
                model=p.model,
                temperature=temperature,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return (resp.choices[0].message.content or "").strip(), p.name
        except Exception as e:  # noqa: BLE001 — provider failures are expected; fall through
            log.warning("LLM provider %s failed: %s", p.name, e)
            errors.append(f"{p.name}: {type(e).__name__}")
            continue
    raise RuntimeError("All configured LLM providers failed: " + " | ".join(errors))
