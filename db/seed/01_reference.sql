-- Reference data: AYUSH systems, languages, and the source registry.
-- Idempotent (ON CONFLICT DO NOTHING).

insert into system (code, name) values
  ('ayurveda',   'Ayurveda'),
  ('unani',      'Unani'),
  ('siddha',     'Siddha'),
  ('sowa_rigpa', 'Sowa Rigpa'),
  ('yoga',       'Yoga & Naturopathy')
on conflict (code) do nothing;

insert into language (code, name, script) values
  ('san', 'Sanskrit',   'Devanagari'),
  ('hin', 'Hindi',      'Devanagari'),
  ('tam', 'Tamil',      'Tamil'),
  ('urd', 'Urdu',       'Arabic'),
  ('ara', 'Arabic',     'Arabic'),
  ('fas', 'Persian',    'Arabic'),
  ('bod', 'Tibetan',    'Tibetan'),
  ('mal', 'Malayalam',  'Malayalam'),
  ('tel', 'Telugu',     'Telugu'),
  ('kan', 'Kannada',    'Kannada'),
  ('eng', 'English',    'Latin')
on conflict (code) do nothing;

-- Source registry mirrors config/sources.yaml. Keep both in sync; the YAML is
-- canonical for ETL, this table is the DB-side join target for provenance.
insert into source (short_code, name, kind, publisher, url, license, is_redistributable) values
  ('imppat',  'IMPPAT 2.0', 'database', 'IMSc Chennai',
     'https://cb.imsc.res.in/imppat/', 'Academic use — verify', false),
  ('duke',    'Dr. Duke''s Phytochemical and Ethnobotanical Databases', 'database', 'USDA ARS',
     'https://phytochem.nal.usda.gov/', 'Public domain (US gov) — verify', true),
  ('pubchem', 'PubChem', 'database', 'NCBI / NLM',
     'https://pubchem.ncbi.nlm.nih.gov/', 'Public domain', true),
  ('powo',    'Plants of the World Online', 'ontology', 'RBG Kew',
     'https://powo.science.kew.org/', 'CC BY 3.0', true),
  ('wfo',     'World Flora Online', 'ontology', 'WFO Consortium',
     'https://www.worldfloraonline.org/', 'CC BY 4.0', true),
  ('api_ayur','Ayurvedic Pharmacopoeia / Formulary of India', 'pharmacopoeia', 'Ministry of AYUSH',
     'https://www.ayush.gov.in/', 'Govt-published — verify', false),
  ('icd11',   'ICD-11 (incl. TM2)', 'ontology', 'WHO',
     'https://icd.who.int/', 'WHO licence — verify', false),
  ('mesh',    'Medical Subject Headings (MeSH)', 'ontology', 'US NLM',
     'https://www.nlm.nih.gov/mesh/', 'Public domain', true)
on conflict (short_code) do nothing;
