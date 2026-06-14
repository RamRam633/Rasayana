# Design decisions

| # | Decision | Choice | Trade-off |
|---|---|---|---|
| D1 | Provenance granularity | `source_id` + `confidence` + `provenance` jsonb per edge | Simple & queryable; claim-level reification (nanopublications) is a later migration |
| D2 | Entity resolution | Canonical-ID-first, non-destructive: InChIKey (chem), accepted name via GBIF/POWO/WFO (plants); confidence + curation queue | Some entities sit unresolved rather than being force-merged |
| D3 | Controlled vocabularies | ICD-11 (incl. TM2) + MeSH for indications; curated seed for rasa/guna/virya/vipaka/dosha | Build small vocab now; full ontology alignment is ongoing |
| D4 | Medical-claims safety | Evidence-tagged, cite-only, persistent disclaimer | Minor UX friction; large ethics/liability win |
| D5 | Text-to-SQL safety | Read-only `vayu_ro` role + statement timeout + static guard + schema allow-list | Slightly more setup; closes injection footguns |
| D6 | Data layering | Bronze (raw, immutable) → Silver (normalized) → Gold (views) | More steps/storage; full reproducibility |
| D7 | Multilingual names | Native script + transliteration + language tag per name | More per-row data; cross-system search works |

## Why Postgres-relational (not a native graph DB)
Aligns with Supabase + the text-to-SQL goal: the schema the LLM reasons over is
the schema we run. Deep traversals use recursive CTEs / join views instead of
Cypher. Apache AGE remains an option if traversal ergonomics become a bottleneck.

## Sources & licensing
`config/sources.yaml` is the registry; `source.is_redistributable` is the gate.
Phase 1 = IMPPAT + Duke + PubChem + POWO/WFO (structured, verifiable). Phase 2 =
pharmacopoeia formulations from PDFs (drafts until curated). TKDL is access-
restricted to patent offices and is **not** ingested.
