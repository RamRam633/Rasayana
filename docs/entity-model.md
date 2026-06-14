# Entity model

Provenance-first property graph realized in Postgres (see `db/schema.sql`).

## Core entities
- **plant** — accepted scientific name + family + external IDs (POWO/WFO/GBIF/IMPPAT/NCBI).
  Generalizable to mineral/animal substances via `kind` (Rasa Shastra, Unani).
- **plant_name** — synonyms + vernacular names (Sanskrit/Hindi/Tamil/Urdu/Tibetan…),
  each with language, script, and transliteration. *The anti-fragmentation table.*
- **phytochemical** — canonical key **InChIKey**; plus PubChem CID, SMILES, formula, class.
- **formulation** — compound preparation; system, dosage form, classical reference, prep.
- **therapeutic_use** — indication/action controlled vocab; maps to ICD-11 (incl. TM2) + MeSH.

## Edges (each carries `source_id` + `confidence` + `provenance`)
| Edge | Meaning | Notable attributes |
|---|---|---|
| `plant_phytochemical` | plant contains chemical | plant_part, evidence |
| `plant_use` | plant used for indication | system, plant_part, evidence |
| `formulation_ingredient` | formulation includes plant/substance | part_used, quantity, proportion, role |
| `formulation_use` | formulation indicated for | evidence |
| `phytochemical_activity` | chemical has bioactivity | target, value |
| `entity_property` | plant/formulation has Ayurvedic property | rasa/guna/virya/vipaka/dosha |
| `xref` | entity ↔ external DB id | confidence |

## Provenance & layering
Every assertion is one row per source, so multi-source and conflicting claims
coexist. `source.is_redistributable` gates serving. Data flows
**bronze (raw) → silver (normalized) → gold (views)**; `is_curated` marks
PDF-extracted drafts pending review.

## RAG
`document` (narrative text, optionally anchored to an entity) → `chunk`
(text + `vector(1024)` embedding) for semantic retrieval via pgvector.
