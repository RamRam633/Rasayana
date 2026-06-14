#!/usr/bin/env bash
# Load the local `vayu` knowledge graph into a managed Postgres (Neon) and, optionally,
# create a select-only role for the Ask (text-to-SQL) path.
#
# The connection string is a SECRET: pass it via env, never commit it.
#   NEON_DATABASE_URL='postgresql://USER:PASS@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require' \
#   RO_PASSWORD='<optional, to create a read-only role>' \
#   bash scripts/load_neon.sh
#
# After it finishes, set these in Vercel (Project Settings > Environment Variables):
#   DATABASE_URL      = postgresql+psycopg://USER:PASS@HOST/neondb?sslmode=require
#   DATABASE_URL_RO   = postgresql+psycopg://vayu_ro:RO_PASSWORD@HOST/neondb?sslmode=require  (if created)
#   plus the LLM keys already in your local .env (CEREBRAS_API_KEY, MISTRAL_API_KEY, ...).
set -euo pipefail

: "${NEON_DATABASE_URL:?set NEON_DATABASE_URL (the Neon connection string; do not commit it)}"
DUMP="${TMPDIR:-/tmp}/vayu.dump"

echo "1/3  Dumping local 'vayu' (custom format, no owner/privileges)..."
pg_dump --no-owner --no-privileges --format=custom --file="$DUMP" vayu
echo "     dump: $(du -h "$DUMP" | cut -f1)"

echo "2/3  Restoring into Neon (this is the slow step)..."
# --clean/--if-exists makes re-runs idempotent; extension notices are harmless.
pg_restore --no-owner --no-privileges --clean --if-exists --exit-on-error=0 \
  --dbname="$NEON_DATABASE_URL" "$DUMP" 2>&1 | grep -viE 'already exists|does not exist|warning: ' || true

if [ -n "${RO_PASSWORD:-}" ]; then
  echo "3/3  Creating select-only role vayu_ro..."
  psql "$NEON_DATABASE_URL" -v ON_ERROR_STOP=1 <<SQL
do \$\$ begin
  if not exists (select from pg_roles where rolname = 'vayu_ro') then
    execute format('create role vayu_ro login password %L', '${RO_PASSWORD}');
  end if;
end \$\$;
grant usage on schema public to vayu_ro;
grant select on all tables in schema public to vayu_ro;
alter default privileges in schema public grant select on tables to vayu_ro;
SQL
  echo "     vayu_ro ready. Use it in DATABASE_URL_RO."
else
  echo "3/3  Skipping read-only role (no RO_PASSWORD set)."
  echo "     The Ask path will use DATABASE_URL with the static SELECT-only guardrails in nlsql.py."
fi

echo "Done. Verify:  psql \"\$NEON_DATABASE_URL\" -c 'select count(*) from plant;'   (expect 9291)"
