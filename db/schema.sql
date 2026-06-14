-- Vayu Materia — knowledge graph schema (Postgres + pgvector)
--
-- Conventions
--   * UUID primary keys (pgcrypto.gen_random_uuid)
--   * Every association/edge row carries source_id + confidence + provenance(jsonb)
--   * This file is the SILVER/GOLD model. BRONZE = immutable raw_* (loaded ad hoc).
--   * Designed for a fresh DB. Re-apply via `make db-reset`.
--   * A read-only role (db/roles.sql) backs the text-to-SQL path.

create extension if not exists pgcrypto;   -- gen_random_uuid()
create extension if not exists vector;      -- pgvector (embeddings)
create extension if not exists pg_trgm;     -- fuzzy / multilingual name search

-- ── enums ───────────────────────────────────────────────────────────────────
create type substance_kind      as enum ('plant','mineral','animal','fungal','other');
create type name_kind           as enum ('scientific_accepted','scientific_synonym','sanskrit','vernacular','trade','other');
create type evidence_level      as enum ('traditional','ethnobotanical','preclinical','clinical','unknown');
create type indication_category as enum ('disease','symptom','action','contraindication');
create type ingredient_role     as enum ('primary','adjuvant','anupana','preservative','excipient','unknown');
create type ayur_property_kind  as enum ('rasa','guna','virya','vipaka','dosha_effect','prabhava','karma');
create type source_kind         as enum ('database','pharmacopoeia','classical_text','article','web','ontology');

-- ── reference ───────────────────────────────────────────────────────────────
create table source (
  id                uuid primary key default gen_random_uuid(),
  short_code        text unique not null,
  name              text not null,
  kind              source_kind not null,
  publisher         text,
  url               text,
  license           text,                         -- NULL = unknown => treat as non-redistributable
  license_url       text,
  version           text,
  retrieved_at      date,
  is_redistributable boolean not null default false,  -- compliance gate for serving
  notes             text,
  created_at        timestamptz not null default now()
);

create table system (                              -- AYUSH systems
  id   uuid primary key default gen_random_uuid(),
  code text unique not null,                        -- ayurveda|unani|siddha|sowa_rigpa|yoga
  name text not null
);

create table language (
  code   text primary key,                          -- ISO 639-3 (san,hin,tam,urd,bod,eng,…)
  name   text not null,
  script text                                        -- Devanagari, Tamil, Arabic, Tibetan, Latin
);

-- ── core entities ───────────────────────────────────────────────────────────
create table plant (
  id                    uuid primary key default gen_random_uuid(),
  kind                  substance_kind not null default 'plant',
  accepted_name         text not null,              -- resolved accepted scientific name
  genus                 text,
  species               text,
  family                text,
  rank                  text,
  powo_id               text,
  wfo_id                text,
  gbif_id               text,
  ncbi_taxid            integer,
  imppat_id             text,
  resolution_confidence real,                        -- 0..1 from the name resolver; NULL = unresolved
  is_curated            boolean not null default false,
  source_id             uuid references source(id),
  created_at            timestamptz not null default now(),
  unique (accepted_name, kind)
);
create index plant_name_trgm on plant using gin (accepted_name gin_trgm_ops);

create table plant_name (                            -- synonyms + vernacular (anti-fragmentation)
  id              uuid primary key default gen_random_uuid(),
  plant_id        uuid not null references plant(id) on delete cascade,
  name            text not null,
  name_kind       name_kind not null,
  language_code   text references language(code),
  script          text,
  transliteration text,                              -- e.g. IAST for Sanskrit
  is_preferred    boolean not null default false,
  source_id       uuid references source(id),
  confidence      real
);
create index plant_name_name_trgm on plant_name using gin (name gin_trgm_ops);
create index plant_name_plant_idx on plant_name (plant_id);

create table phytochemical (
  id                 uuid primary key default gen_random_uuid(),
  preferred_name     text,
  inchikey           text unique,                    -- canonical key (27-char InChIKey)
  inchi              text,
  smiles             text,
  molecular_formula  text,
  molecular_weight   real,
  pubchem_cid        bigint,
  chebi_id           text,
  chembl_id          text,
  np_class           text,                           -- NPClassifier / ClassyFire
  drug_likeness      jsonb,
  source_id          uuid references source(id),
  created_at         timestamptz not null default now()
);
create index phytochemical_cid_idx on phytochemical (pubchem_cid);

create table therapeutic_use (                       -- indication / action (controlled vocab)
  id             uuid primary key default gen_random_uuid(),
  preferred_label text not null,
  category       indication_category not null default 'disease',
  system_term    text,                               -- original term, e.g. 'Jvara'
  system_id      uuid references system(id),
  icd11_code     text,                               -- incl. TM2 module
  mesh_id        text,
  description    text,
  source_id      uuid references source(id),
  unique (preferred_label, category)
);
create index therapeutic_use_trgm on therapeutic_use using gin (preferred_label gin_trgm_ops);

create table formulation (
  id                 uuid primary key default gen_random_uuid(),
  name               text not null,
  system_id          uuid references system(id),
  dosage_form        text,                            -- churna, kwatha, taila, asava, majun, …
  classical_reference text,                           -- text + chapter/verse
  preparation_method text,
  is_curated         boolean not null default false,  -- PDF-extracted => false until reviewed
  source_id          uuid references source(id),
  created_at         timestamptz not null default now()
);
create index formulation_trgm on formulation using gin (name gin_trgm_ops);

-- ── association / edge tables (each carries provenance) ─────────────────────
create table plant_phytochemical (
  id               uuid primary key default gen_random_uuid(),
  plant_id         uuid not null references plant(id) on delete cascade,
  phytochemical_id uuid not null references phytochemical(id) on delete cascade,
  plant_part       text,
  evidence         evidence_level not null default 'unknown',
  confidence       real,
  source_id        uuid not null references source(id),
  provenance       jsonb,
  unique (plant_id, phytochemical_id, plant_part, source_id)
);
create index ppc_phyto_idx on plant_phytochemical (phytochemical_id);

create table plant_use (
  id                 uuid primary key default gen_random_uuid(),
  plant_id           uuid not null references plant(id) on delete cascade,
  therapeutic_use_id uuid not null references therapeutic_use(id) on delete cascade,
  system_id          uuid references system(id),
  plant_part         text,
  evidence           evidence_level not null default 'traditional',
  confidence         real,
  source_id          uuid not null references source(id),
  provenance         jsonb,
  unique (plant_id, therapeutic_use_id, system_id, source_id)
);
create index plant_use_use_idx on plant_use (therapeutic_use_id);

create table formulation_ingredient (
  id             uuid primary key default gen_random_uuid(),
  formulation_id uuid not null references formulation(id) on delete cascade,
  plant_id       uuid references plant(id),          -- nullable: ingredient may be unresolved
  ingredient_text text,                              -- raw ingredient string as written
  part_used      text,
  quantity_value numeric,
  quantity_unit  text,
  proportion     real,
  role           ingredient_role not null default 'unknown',
  processing     text,                                -- shodhana / bhavana / etc.
  source_id      uuid not null references source(id),
  provenance     jsonb
);
create index fi_form_idx  on formulation_ingredient (formulation_id);
create index fi_plant_idx on formulation_ingredient (plant_id);

create table formulation_use (
  id                 uuid primary key default gen_random_uuid(),
  formulation_id     uuid not null references formulation(id) on delete cascade,
  therapeutic_use_id uuid not null references therapeutic_use(id) on delete cascade,
  evidence           evidence_level not null default 'traditional',
  confidence         real,
  source_id          uuid not null references source(id),
  provenance         jsonb,
  unique (formulation_id, therapeutic_use_id, source_id)
);

create table phytochemical_activity (
  id               uuid primary key default gen_random_uuid(),
  phytochemical_id uuid not null references phytochemical(id) on delete cascade,
  activity         text not null,                     -- e.g. 'anti-inflammatory'
  target           text,                              -- protein/gene target if known
  value_text       text,                              -- raw measured value + units
  evidence         evidence_level not null default 'preclinical',
  confidence       real,
  source_id        uuid not null references source(id),
  provenance       jsonb
);
create index pa_phyto_idx on phytochemical_activity (phytochemical_id);

-- ── Ayurvedic pharmacology (rasa/guna/virya/vipaka/dosha) ───────────────────
create table property_term (                          -- controlled vocab
  id              uuid primary key default gen_random_uuid(),
  kind            ayur_property_kind not null,
  value           text not null,                      -- e.g. 'madhura', 'ushna'
  transliteration text,
  gloss           text,                                -- english gloss
  unique (kind, value)
);

create table entity_property (                         -- polymorphic: plant or formulation
  id               uuid primary key default gen_random_uuid(),
  entity_type      text not null check (entity_type in ('plant','formulation')),
  entity_id        uuid not null,
  property_term_id uuid not null references property_term(id),
  source_id        uuid references source(id),
  provenance       jsonb                                -- e.g. {"dosha_effect":"decrease"}
);
create index entity_property_idx on entity_property (entity_type, entity_id);

-- ── generic external cross-reference ────────────────────────────────────────
create table xref (
  id          uuid primary key default gen_random_uuid(),
  entity_type text not null,                            -- plant|phytochemical|formulation|therapeutic_use
  entity_id   uuid not null,
  external_db text not null,                            -- powo|wfo|gbif|pubchem|chebi|chembl|imppat|wikidata
  external_id text not null,
  url         text,
  confidence  real,
  unique (entity_type, entity_id, external_db, external_id)
);
create index xref_entity_idx on xref (entity_type, entity_id);

-- ── RAG layer ───────────────────────────────────────────────────────────────
create table document (
  id          uuid primary key default gen_random_uuid(),
  source_id   uuid references source(id),
  title       text,
  entity_type text,                                     -- optional anchor to an entity
  entity_id   uuid,
  url         text,
  raw_text    text,
  lang_code   text references language(code),
  created_at  timestamptz not null default now()
);

create table chunk (
  id          uuid primary key default gen_random_uuid(),
  document_id uuid not null references document(id) on delete cascade,
  ord         integer not null,
  text        text not null,
  embedding   vector(1024),                             -- keep in sync with EMBEDDING_DIM
  metadata    jsonb,
  unique (document_id, ord)
);
-- Build the ANN index after bulk load. HNSW = good recall without tuning lists.
create index chunk_embedding_hnsw on chunk using hnsw (embedding vector_cosine_ops);
