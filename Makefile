.DEFAULT_GOAL := help
PY       ?= .venv/bin/python
PIP      ?= .venv/bin/pip
PG_BIN   ?= /opt/homebrew/opt/postgresql@17/bin
PGDATA   ?= /opt/homebrew/var/postgresql@17
PSQL_URL ?= postgresql://localhost:5432/vayu
export LC_ALL ?= en_US.UTF-8          # avoids "postmaster became multithreaded" on macOS

.PHONY: help setup db-start db-stop db-schema db-reset seed api ui mcp etl test lint fmt

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Create venv (Python 3.11) + install deps
	/opt/homebrew/bin/python3.11 -m venv .venv
	$(PIP) install -U pip wheel
	$(PIP) install -e ".[mcp,ui,dev]" openai

db-start: ## Start local Homebrew Postgres 17 + ensure the 'vayu' database
	@$(PG_BIN)/pg_isready -q -h localhost || \
	  $(PG_BIN)/pg_ctl -D $(PGDATA) -l /tmp/vayu_pg.log -w start
	@$(PG_BIN)/createdb -h localhost vayu 2>/dev/null && echo "created db 'vayu'" || echo "db 'vayu' ready"

db-stop: ## Stop local Postgres
	@$(PG_BIN)/pg_ctl -D $(PGDATA) -m fast stop || true

db-schema: ## Apply schema + views + seeds + read-only role
	$(PG_BIN)/psql "$(PSQL_URL)" -v ON_ERROR_STOP=1 -f db/schema.sql
	$(PG_BIN)/psql "$(PSQL_URL)" -v ON_ERROR_STOP=1 -f db/views.sql
	@for f in db/seed/*.sql; do $(PG_BIN)/psql "$(PSQL_URL)" -v ON_ERROR_STOP=1 -f $$f; done
	$(PG_BIN)/psql "$(PSQL_URL)" -v ON_ERROR_STOP=1 -f db/roles.sql

db-reset: ## Drop + recreate the public schema, then re-apply
	$(PG_BIN)/psql "$(PSQL_URL)" -c "drop schema public cascade; create schema public;"
	$(MAKE) db-schema

seed: ## Load the curated demo dataset (live GBIF + PubChem)
	$(PY) -m vayu.cli seed-demo

api: ## Run the FastAPI core (http://localhost:8000, /docs for OpenAPI)
	.venv/bin/uvicorn vayu.api.main:app --reload --port 8000

ui: ## Run the legacy Streamlit UI (http://localhost:8501)
	.venv/bin/streamlit run ui/app.py

web-install: ## Install the Rasayana web app deps
	npm --prefix web install

web: ## Run the Rasayana web app (Vite, http://localhost:5173 — needs `make api`)
	npm --prefix web run dev

mcp: ## Run the MCP server (stdio) for Claude Desktop
	$(PY) -m mcp_server.server

etl: ## Run a source pipeline:  make etl SOURCE=pubchem ARGS="--name 'curcumin'"
	$(PY) -m vayu.cli ingest $(SOURCE) $(ARGS)

test: ## Run tests
	$(PY) -m pytest -q

lint: ## Lint + typecheck
	.venv/bin/ruff check . && .venv/bin/mypy vayu

fmt: ## Format
	.venv/bin/ruff format . && .venv/bin/ruff check --fix .
