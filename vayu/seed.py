"""Curated demo seed — a small, accurate, fully-sourced slice of the graph.

Plants are resolved live via GBIF and chemicals live via PubChem (this exercises
the real pipeline and gives canonical IDs). The *relationships* between them are
hand-curated and attributed to the `vayu_seed` source with explicit evidence
levels and a `{"note":"curated demo seed"}` provenance — so nothing is presented
as if a source asserted something it didn't. Idempotent.

Run: vayu seed-demo
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict

from sqlalchemy import text
from sqlalchemy.orm import Session

from vayu import db
from vayu.etl.extract.pubchem import PubChemExtractor
from vayu.models import PlantRecord
from vayu.normalize import BotanicalResolver

log = logging.getLogger("vayu.seed")

# (scientific, IAST, Devanagari, English common)
PLANTS = [
    ("Withania somnifera", "aśvagandhā", "अश्वगंधा", "Ashwagandha"),
    ("Curcuma longa", "haridrā", "हरिद्रा", "Turmeric"),
    ("Ocimum tenuiflorum", "tulasī", "तुलसी", "Holy basil"),
    ("Azadirachta indica", "nimba", "निम्ब", "Neem"),
    ("Bacopa monnieri", "brāhmī", "ब्राह्मी", "Brahmi"),
    ("Tinospora cordifolia", "guḍūcī", "गुडूची", "Guduchi"),
    ("Phyllanthus emblica", "āmalakī", "आमलकी", "Indian gooseberry"),
    ("Terminalia chebula", "harītakī", "हरीतकी", "Chebulic myrobalan"),
    ("Terminalia bellirica", "bibhītakī", "बिभीतकी", "Bibhitaki"),
    ("Zingiber officinale", "śuṇṭhī", "शुण्ठी", "Ginger"),
    ("Piper longum", "pippalī", "पिप्पली", "Long pepper"),
    ("Piper nigrum", "marica", "मरिच", "Black pepper"),
]

CHEMICALS = [
    "Withaferin A", "Curcumin", "Eugenol", "Azadirachtin", "Columbin",
    "Gallic acid", "Ellagic acid", "Chebulagic acid", "6-Gingerol", "Piperine",
]

PLANT_CHEMICALS = {
    "Withania somnifera": ["Withaferin A"],
    "Curcuma longa": ["Curcumin"],
    "Ocimum tenuiflorum": ["Eugenol"],
    "Azadirachta indica": ["Azadirachtin"],
    "Tinospora cordifolia": ["Columbin"],
    "Phyllanthus emblica": ["Gallic acid", "Ellagic acid"],
    "Terminalia chebula": ["Chebulagic acid", "Gallic acid"],
    "Terminalia bellirica": ["Gallic acid", "Ellagic acid"],
    "Zingiber officinale": ["6-Gingerol", "Eugenol"],
    "Piper longum": ["Piperine"],
    "Piper nigrum": ["Piperine"],
}

# (label, category, system_term)
USES = [
    ("Fever", "disease", "Jvara"),
    ("Cough", "symptom", "Kasa"),
    ("Inflammation", "symptom", "Shotha"),
    ("Diabetes mellitus", "disease", "Prameha"),
    ("Rejuvenation (Rasayana)", "action", "Rasayana"),
    ("Indigestion", "symptom", "Agnimandya"),
]

PLANT_USES = {
    "Withania somnifera": ["Rejuvenation (Rasayana)"],
    "Tinospora cordifolia": ["Fever", "Rejuvenation (Rasayana)"],
    "Ocimum tenuiflorum": ["Cough", "Fever"],
    "Curcuma longa": ["Inflammation"],
    "Phyllanthus emblica": ["Rejuvenation (Rasayana)", "Diabetes mellitus"],
    "Zingiber officinale": ["Cough", "Indigestion"],
    "Azadirachta indica": ["Inflammation"],
    "Piper longum": ["Cough"],
}

FORMULATIONS = [
    {
        "name": "Triphala",
        "dosage_form": "Churna",
        "classical_reference": "Sharngadhara Samhita",
        "ingredients": [
            ("Phyllanthus emblica", "primary"),
            ("Terminalia chebula", "primary"),
            ("Terminalia bellirica", "primary"),
        ],
        "uses": ["Rejuvenation (Rasayana)", "Indigestion"],
    },
    {
        "name": "Trikatu",
        "dosage_form": "Churna",
        "classical_reference": "Sharngadhara Samhita",
        "ingredients": [
            ("Zingiber officinale", "primary"),
            ("Piper longum", "primary"),
            ("Piper nigrum", "primary"),
        ],
        "uses": ["Cough", "Indigestion"],
    },
]

# scientific -> [(kind, value, dosha_direction_or_None)]
PROPERTIES = {
    "Withania somnifera": [
        ("rasa", "tikta", None), ("rasa", "kashaya", None),
        ("virya", "ushna", None), ("vipaka", "madhura", None),
        ("dosha_effect", "vata", "decrease"), ("dosha_effect", "kapha", "decrease"),
    ],
    "Zingiber officinale": [
        ("rasa", "katu", None), ("virya", "ushna", None), ("vipaka", "madhura", None),
        ("dosha_effect", "vata", "decrease"), ("dosha_effect", "kapha", "decrease"),
    ],
    "Curcuma longa": [
        ("rasa", "tikta", None), ("rasa", "katu", None),
        ("virya", "ushna", None), ("dosha_effect", "kapha", "decrease"),
    ],
}

_CURATED = json.dumps({"note": "curated demo seed"})


def _scalar(s: Session, sql: str, **p):
    return s.execute(text(sql), p).scalar()


def _exec(s: Session, sql: str, **p):
    s.execute(text(sql), p)


def _ensure_source(s: Session) -> str:
    return _scalar(s, """
        insert into source (short_code, name, kind, publisher, license, is_redistributable)
        values ('vayu_seed', 'Vayu Materia curated demo seed', 'database',
                'Vayu Materia', 'CC BY 4.0 (curated)', true)
        on conflict (short_code) do update set name = excluded.name
        returning id
    """)


def _plant(s, src, resolver, sci, iast, deva, eng) -> str:
    rec = resolver.resolve(PlantRecord(raw_name=sci, source_code="vayu_seed"))
    accepted = rec.accepted_name or sci
    pid = _scalar(s, """
        insert into plant (accepted_name, genus, family, gbif_id,
                           resolution_confidence, is_curated, source_id)
        values (:an, :g, :f, :gb, :rc, true, :src)
        on conflict (accepted_name, kind) do update set
          family  = coalesce(plant.family, excluded.family),
          gbif_id = coalesce(plant.gbif_id, excluded.gbif_id)
        returning id
    """, an=accepted, g=rec.genus, f=rec.family, gb=rec.gbif_id,
        rc=rec.resolution_confidence, src=src)
    _name(s, src, pid, deva, "sanskrit", "san", "Devanagari", iast, True)
    _name(s, src, pid, eng, "vernacular", "eng", "Latin", None, False)
    return pid


def _name(s, src, pid, name, kind, lang, script, translit, pref):
    _exec(s, """
        insert into plant_name (plant_id, name, name_kind, language_code, script,
                                transliteration, is_preferred, source_id)
        select :pid, :name, :kind, :lang, :script, :tr, :pref, :src
        where not exists (select 1 from plant_name
                          where plant_id = :pid and name = :name and name_kind = :kind)
    """, pid=pid, name=name, kind=kind, lang=lang, script=script, tr=translit,
        pref=pref, src=src)


def _chem(s, src, pubchem, name) -> str | None:
    rec = pubchem.by_name(name)
    if rec is None or not rec.inchikey:
        log.warning("PubChem could not resolve %r — skipping (no fabricated row)", name)
        return None
    return _scalar(s, """
        insert into phytochemical (preferred_name, inchikey, inchi, smiles,
                                   molecular_formula, molecular_weight, pubchem_cid, source_id)
        values (:pn, :ik, :inchi, :smi, :mf, :mw, :cid, :src)
        on conflict (inchikey) do update set
          preferred_name = coalesce(phytochemical.preferred_name, excluded.preferred_name),
          pubchem_cid    = coalesce(phytochemical.pubchem_cid, excluded.pubchem_cid)
        returning id
    """, pn=name, ik=rec.inchikey, inchi=rec.inchi, smi=rec.smiles,
        mf=rec.molecular_formula, mw=rec.molecular_weight, cid=rec.pubchem_cid, src=src)


def _ppc(s, src, pid, cid, evidence):
    _exec(s, """
        insert into plant_phytochemical (plant_id, phytochemical_id, evidence,
                                         source_id, provenance)
        select :pid, :cid, :ev, :src, cast(:prov as jsonb)
        where not exists (select 1 from plant_phytochemical
                          where plant_id = :pid and phytochemical_id = :cid and source_id = :src)
    """, pid=pid, cid=cid, ev=evidence, src=src, prov=_CURATED)


def _use(s, src, label, category, system_term) -> str:
    return _scalar(s, """
        insert into therapeutic_use (preferred_label, category, system_term, system_id, source_id)
        values (:lbl, :cat, :st, (select id from system where code='ayurveda'), :src)
        on conflict (preferred_label, category) do update set
          system_term = coalesce(therapeutic_use.system_term, excluded.system_term)
        returning id
    """, lbl=label, cat=category, st=system_term, src=src)


def _plant_use(s, src, pid, uid, evidence):
    _exec(s, """
        insert into plant_use (plant_id, therapeutic_use_id, system_id, evidence,
                               source_id, provenance)
        select :pid, :uid, (select id from system where code='ayurveda'), :ev, :src,
               cast(:prov as jsonb)
        where not exists (select 1 from plant_use
                          where plant_id = :pid and therapeutic_use_id = :uid and source_id = :src)
    """, pid=pid, uid=uid, ev=evidence, src=src, prov=_CURATED)


def _formulation(s, src, f) -> str:
    fid = _scalar(s, """
        insert into formulation (name, system_id, dosage_form, classical_reference,
                                 is_curated, source_id)
        select :name, (select id from system where code='ayurveda'), :df, :cr, true, :src
        where not exists (select 1 from formulation where name = :name)
        returning id
    """, name=f["name"], df=f["dosage_form"], cr=f["classical_reference"], src=src)
    return fid or _scalar(s, "select id from formulation where name = :name", name=f["name"])


def _ingredient(s, src, fid, pid, txt, role):
    _exec(s, """
        insert into formulation_ingredient (formulation_id, plant_id, ingredient_text,
                                            role, source_id, provenance)
        select :fid, :pid, :txt, :role, :src, cast(:prov as jsonb)
        where not exists (select 1 from formulation_ingredient
                          where formulation_id = :fid and plant_id = :pid)
    """, fid=fid, pid=pid, txt=txt, role=role, src=src, prov=_CURATED)


def _formulation_use(s, src, fid, uid):
    _exec(s, """
        insert into formulation_use (formulation_id, therapeutic_use_id, evidence,
                                     source_id, provenance)
        select :fid, :uid, 'traditional', :src, cast(:prov as jsonb)
        where not exists (select 1 from formulation_use
                          where formulation_id = :fid and therapeutic_use_id = :uid and source_id = :src)
    """, fid=fid, uid=uid, src=src, prov=_CURATED)


def _property(s, src, pid, kind, value, direction):
    pt = _scalar(s, "select id from property_term where kind = :k and value = :v",
                 k=kind, v=value)
    if not pt:
        return
    prov = json.dumps({"dosha_effect": direction}) if direction else _CURATED
    _exec(s, """
        insert into entity_property (entity_type, entity_id, property_term_id,
                                     source_id, provenance)
        select 'plant', :pid, :pt, :src, cast(:prov as jsonb)
        where not exists (select 1 from entity_property
                          where entity_type='plant' and entity_id = :pid and property_term_id = :pt)
    """, pid=pid, pt=pt, src=src, prov=prov)


def seed_demo() -> dict:
    resolver = BotanicalResolver()
    pubchem = PubChemExtractor()
    counts: dict[str, int] = defaultdict(int)

    with db.session() as s:
        src = _ensure_source(s)

        plant_ids: dict[str, str] = {}
        for sci, iast, deva, eng in PLANTS:
            plant_ids[sci] = _plant(s, src, resolver, sci, iast, deva, eng)
            counts["plants"] += 1

        chem_ids: dict[str, str] = {}
        for name in CHEMICALS:
            cid = _chem(s, src, pubchem, name)
            if cid:
                chem_ids[name] = cid
                counts["chemicals"] += 1
            else:
                counts["chemicals_unresolved"] += 1

        for sci, chems in PLANT_CHEMICALS.items():
            for cname in chems:
                if sci in plant_ids and cname in chem_ids:
                    _ppc(s, src, plant_ids[sci], chem_ids[cname], "preclinical")
                    counts["plant_chemical_edges"] += 1

        use_ids = {lbl: _use(s, src, lbl, cat, st) for lbl, cat, st in USES}
        counts["uses"] = len(use_ids)
        for sci, uses in PLANT_USES.items():
            for lbl in uses:
                _plant_use(s, src, plant_ids[sci], use_ids[lbl], "traditional")
                counts["plant_use_edges"] += 1

        for f in FORMULATIONS:
            fid = _formulation(s, src, f)
            counts["formulations"] += 1
            for sci, role in f["ingredients"]:
                if sci in plant_ids:
                    _ingredient(s, src, fid, plant_ids[sci], sci, role)
                    counts["ingredients"] += 1
            for lbl in f["uses"]:
                if lbl in use_ids:
                    _formulation_use(s, src, fid, use_ids[lbl])
                    counts["formulation_use_edges"] += 1

        for sci, props in PROPERTIES.items():
            for kind, value, direction in props:
                _property(s, src, plant_ids[sci], kind, value, direction)
                counts["properties"] += 1

    return dict(counts)
