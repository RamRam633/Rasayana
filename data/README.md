# data/ — the medallion lake (gitignored)

Ingested data is **never committed** (license + size). This tree is local scratch.

- `raw/` — **bronze**: source dumps exactly as downloaded, immutable.
  Organize by source: `raw/imppat/`, `raw/duke/`, `raw/pharmacopoeia/`.
- `interim/` — **silver**: normalized / entity-resolved intermediates.
- `processed/` — **gold**: curated extracts ready to load (or already loaded).

Provenance (where each file came from, when, under what license) is tracked in
`config/sources.yaml`, not here.
