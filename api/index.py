"""Vercel Python serverless entrypoint for the Rasayana API.

The Vite frontend calls `/api/*` (same origin). A `vercel.json` rewrite routes every
`/api/*` request to this function. The real FastAPI app (vayu.api.main) defines its
routes at the root (`/stats`, `/chat`, ...), so we mount it under `/api` here. That keeps
one app, one schema, identical to local, with the prefix added only at the edge.

Config is env-driven (config.settings): set DATABASE_URL (+ optional DATABASE_URL_RO) and
the LLM provider keys as Vercel environment variables. Nothing secret lives in the repo.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the repo root importable so `config` and `vayu` resolve inside the function bundle.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi import FastAPI  # noqa: E402

from vayu.api.main import app as inner_app  # noqa: E402

app = FastAPI(title="Rasayana API (Vercel)")
app.mount("/api", inner_app)
