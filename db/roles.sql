-- Read-only role for the text-to-SQL path. The LLM-generated SQL connects as
-- this role ONLY — it cannot write, DDL, or escalate. Combined with a statement
-- timeout and schema allow-listing in vayu/nlsql.py, this closes the obvious footguns.
--
-- Run as a superuser. Set a real password out-of-band (do not commit it).
-- The database name below ('vayu') matches docker-compose; change for Supabase.

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'vayu_ro') then
    create role vayu_ro login password 'changeme';
  end if;
end
$$;

grant connect on database vayu to vayu_ro;
grant usage on schema public to vayu_ro;
grant select on all tables in schema public to vayu_ro;
alter default privileges in schema public grant select on tables to vayu_ro;

-- Belt and suspenders: ensure no write paths are reachable.
revoke insert, update, delete, truncate on all tables in schema public from vayu_ro;

-- Cap any single statement at 5s for this role (defense against runaway queries).
alter role vayu_ro set statement_timeout = '5s';
