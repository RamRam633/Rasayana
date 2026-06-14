"""Text-to-SQL with guardrails, over the OpenAI-compatible provider chain.

Safety is layered (defense in depth):
  1. Generated SQL runs ONLY as the read-only `vayu_ro` role (db/roles.sql),
     which physically cannot write or DDL, with a 5s statement timeout.
  2. `guard_sql` statically rejects anything that isn't a single SELECT/WITH and
     forces a LIMIT — a prompt-injected DELETE never reaches the DB.
  3. The model sees only the whitelisted schema below.
"""
from __future__ import annotations

import json
import re

from sqlalchemy import text

from vayu import db, llm

SCHEMA_PROMPT = """\
You write a SINGLE read-only Postgres SELECT (or WITH ... SELECT) query.
Only these relations exist:

  source(id, short_code, name, license, is_redistributable)
  system(id, code, name)
  plant(id, accepted_name, family, resolution_confidence, is_curated)
  plant_name(plant_id, name, name_kind, language_code, transliteration)
  phytochemical(id, preferred_name, inchikey, pubchem_cid, molecular_formula)
  therapeutic_use(id, preferred_label, category, system_term, icd11_code)
  formulation(id, name, system_id, dosage_form, is_curated)
  plant_phytochemical(plant_id, phytochemical_id, plant_part, evidence, source_id)
  plant_use(plant_id, therapeutic_use_id, system_id, evidence, source_id)
  formulation_ingredient(formulation_id, plant_id, ingredient_text, part_used, role, source_id)
  formulation_use(formulation_id, therapeutic_use_id, evidence, source_id)
  phytochemical_activity(phytochemical_id, activity, target, evidence, source_id)
  property_term(id, kind, value, gloss)         -- rasa/guna/virya/vipaka/dosha_effect
  entity_property(entity_type, entity_id, property_term_id)
  -- convenience views: v_plant_overview, v_formulation_detail, v_plant_search

Rules: SELECT only; never modify data; always include a LIMIT (<=200);
join `source` when useful so results can cite provenance; phytochemical names are
in phytochemical.preferred_name; plant names in plant.accepted_name and plant_name.name.
Output the SQL inside a ```sql code block, nothing else."""

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy|"
    r"vacuum|attach|merge|call|do|into)\b",
    re.IGNORECASE,
)


def guard_sql(sql: str, max_limit: int = 200) -> str:
    s = sql.strip().rstrip(";").strip()
    if ";" in s:
        raise ValueError("multiple statements are not allowed")
    head = s.lower()
    if not (head.startswith("select") or head.startswith("with")):
        raise ValueError("only SELECT / WITH queries are allowed")
    if _FORBIDDEN.search(s):
        raise ValueError("write/DDL keywords are not allowed")
    if not re.search(r"\blimit\b", head):
        s = f"{s}\nlimit {max_limit}"
    return s


def _extract_sql(raw: str) -> str:
    """Pull SQL out of an LLM reply that may be fenced or prose-wrapped."""
    m = re.search(r"```(?:sql)?\s*(.+?)```", raw, re.S | re.I)
    body = m.group(1) if m else raw
    m2 = re.search(r"\b(select|with)\b", body, re.I)
    if m2:
        body = body[m2.start():]
    return body.split(";")[0].strip()


def run_sql(sql: str) -> list[dict]:
    safe = guard_sql(sql)
    with db.ro_engine().connect() as c:
        c.execute(text("set local statement_timeout = '5s'"))
        return [dict(r) for r in c.execute(text(safe)).mappings().all()]


def generate_sql(question: str) -> tuple[str, str]:
    raw, provider = llm.complete(SCHEMA_PROMPT, question, max_tokens=600)
    return _extract_sql(raw), provider


def ask(question: str) -> dict:
    """Full text-to-SQL turn: generate -> guard -> run."""
    sql, provider = generate_sql(question)
    safe = guard_sql(sql)
    return {"mode": "sql", "sql": safe, "rows": run_sql(safe), "provider": provider}


def synthesize(question: str, rows: list[dict], max_rows: int = 40) -> tuple[str, str]:
    """Turn result rows into a short, cited, non-prescriptive prose answer."""
    system = (
        "You are Vayu, a precise assistant for an Indian traditional-medicine knowledge "
        "graph. Answer ONLY from the provided result rows; do not invent facts. Be concise "
        "(2-4 sentences). If rows are empty, say no matching records were found. This is "
        "traditional/research information, NOT medical advice — give no dosing or treatment "
        "instructions. Mention source short-codes when present."
    )
    user = f"Question: {question}\n\nResult rows (JSON):\n{json.dumps(rows[:max_rows], default=str)}"
    return llm.complete(system, user, max_tokens=350)
