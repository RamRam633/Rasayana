"""LLM access via an OpenAI-compatible provider fallback chain.

Ported from the DeZURIK llm-fallback-framework: providers ordered by
intelligence x reliability, **Cerebras gpt-oss-120b first** (its clean SQL is what
fixes our text-to-SQL accuracy), each *configured* provider tried until one
answers. Surfaces which provider responded. A provider with no key is dropped.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

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
        Provider("cerebras", "https://api.cerebras.ai/v1", s.cerebras_api_key, s.cerebras_model),
        Provider("mistral", "https://api.mistral.ai/v1", s.mistral_api_key, s.mistral_model),
        Provider("groq", "https://api.groq.com/openai/v1", s.groq_api_key, s.groq_model),
        Provider("nvidia", "https://integrate.api.nvidia.com/v1", s.nvidia_api_key, s.nvidia_model),
        Provider("gemini", "https://generativelanguage.googleapis.com/v1beta/openai",
                 s.gemini_api_key, s.gemini_model),
        Provider("openrouter", "https://openrouter.ai/api/v1", s.openrouter_api_key, s.openrouter_model),
    ]
    return [p for p in candidates if p.api_key]


def available() -> list[str]:
    """Configured providers, in fallback order."""
    return [p.name for p in _chain()]


def _client(p: Provider):
    from openai import OpenAI  # lazy
    return OpenAI(base_url=p.base_url, api_key=p.api_key, timeout=60.0)


def complete(system: str, user: str, *, max_tokens: int = 800, temperature: float = 0.0) -> tuple[str, str]:
    """One-shot completion. Returns (text, provider_name)."""
    chain = _chain()
    if not chain:
        raise RuntimeError(
            "No LLM provider configured. Set CEREBRAS_API_KEY / MISTRAL_API_KEY / "
            "GROQ_API_KEY / NVIDIA_API_KEY / GEMINI_API_KEY / OPENROUTER_API_KEY in .env."
        )
    errors: list[str] = []
    for p in chain:
        try:
            resp = _client(p).chat.completions.create(
                model=p.model, temperature=temperature, max_tokens=max_tokens,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text, p.name
            errors.append(f"{p.name}: empty")
        except Exception as e:  # noqa: BLE001 — provider failures fall through by design
            log.warning("LLM provider %s failed: %s", p.name, e)
            errors.append(f"{p.name}: {type(e).__name__}")
    raise RuntimeError("All configured LLM providers failed: " + " | ".join(errors))


def stream(system: str, user: str, *, max_tokens: int = 700, temperature: float = 0.2):
    """Generator yielding ('meta', provider) then ('delta', text)… from the first
    working provider. Powers the streaming assistant."""
    from openai import OpenAI  # noqa: F401  (used via _client)

    chain = _chain()
    if not chain:
        raise RuntimeError("No LLM provider configured (see .env).")
    errors: list[str] = []
    for p in chain:
        try:
            resp = _client(p).chat.completions.create(
                model=p.model, temperature=temperature, max_tokens=max_tokens, stream=True,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            yield ("meta", p.name)
            got = False
            for chunk in resp:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    got = True
                    yield ("delta", delta)
            if got:
                return
            errors.append(f"{p.name}: empty")
        except Exception as e:  # noqa: BLE001
            log.warning("LLM provider %s stream failed: %s", p.name, e)
            errors.append(f"{p.name}: {type(e).__name__}")
    raise RuntimeError("All configured LLM providers failed: " + " | ".join(errors))


def chat(messages: list[dict], *, tools: list | None = None, max_tokens: int = 900,
         temperature: float = 0.0) -> tuple[Any, str]:
    """Lower-level call returning (message, provider). Supports OpenAI tool calling —
    used by the agentic text-to-SQL loop (Phase 5)."""
    chain = _chain()
    if not chain:
        raise RuntimeError("No LLM provider configured (see .env).")
    errors: list[str] = []
    for p in chain:
        try:
            body: dict[str, Any] = {
                "model": p.model, "temperature": temperature,
                "max_tokens": max_tokens, "messages": messages,
            }
            if tools:
                body["tools"] = tools
                body["tool_choice"] = "auto"
            resp = _client(p).chat.completions.create(**body)
            return resp.choices[0].message, p.name
        except Exception as e:  # noqa: BLE001
            log.warning("LLM provider %s failed: %s", p.name, e)
            errors.append(f"{p.name}: {type(e).__name__}")
    raise RuntimeError("All configured LLM providers failed: " + " | ".join(errors))
