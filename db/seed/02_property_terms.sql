-- Ayurvedic pharmacology controlled vocabulary (rasa, guna, virya, vipaka, dosha).
-- Transliteration is IAST; gloss is an approximate English rendering.
-- Idempotent on (kind, value).

insert into property_term (kind, value, transliteration, gloss) values
  -- Rasa (six tastes)
  ('rasa', 'madhura', 'madhura', 'sweet'),
  ('rasa', 'amla',    'amla',    'sour'),
  ('rasa', 'lavana',  'lavaṇa',  'salty'),
  ('rasa', 'katu',    'kaṭu',    'pungent'),
  ('rasa', 'tikta',   'tikta',   'bitter'),
  ('rasa', 'kashaya', 'kaṣāya',  'astringent'),

  -- Virya (potency)
  ('virya', 'ushna', 'uṣṇa', 'heating'),
  ('virya', 'shita', 'śīta', 'cooling'),

  -- Vipaka (post-digestive effect)
  ('vipaka', 'madhura', 'madhura', 'sweet'),
  ('vipaka', 'amla',    'amla',    'sour'),
  ('vipaka', 'katu',    'kaṭu',    'pungent'),

  -- Guna (the twenty qualities, ten complementary pairs)
  ('guna', 'guru',     'guru',     'heavy'),
  ('guna', 'laghu',    'laghu',    'light'),
  ('guna', 'manda',    'manda',    'slow/dull'),
  ('guna', 'tikshna',  'tīkṣṇa',   'sharp/intense'),
  ('guna', 'shita',    'śīta',     'cold'),
  ('guna', 'ushna',    'uṣṇa',     'hot'),
  ('guna', 'snigdha',  'snigdha',  'unctuous/oily'),
  ('guna', 'ruksha',   'rūkṣa',    'dry'),
  ('guna', 'slakshna', 'ślakṣṇa',  'smooth'),
  ('guna', 'khara',    'khara',    'rough'),
  ('guna', 'sandra',   'sāndra',   'dense/solid'),
  ('guna', 'drava',    'drava',    'liquid'),
  ('guna', 'mridu',    'mṛdu',     'soft'),
  ('guna', 'kathina',  'kaṭhina',  'hard'),
  ('guna', 'sthira',   'sthira',   'stable/static'),
  ('guna', 'sara',     'sara',     'mobile/flowing'),
  ('guna', 'sukshma',  'sūkṣma',   'subtle'),
  ('guna', 'sthula',   'sthūla',   'gross/bulky'),
  ('guna', 'vishada',  'viśada',   'clear/non-slimy'),
  ('guna', 'picchila', 'picchila', 'slimy/cloudy'),

  -- Dosha (effect direction recorded in entity_property.provenance)
  ('dosha_effect', 'vata',  'vāta',  'vata'),
  ('dosha_effect', 'pitta', 'pitta', 'pitta'),
  ('dosha_effect', 'kapha', 'kapha', 'kapha')
on conflict (kind, value) do nothing;
