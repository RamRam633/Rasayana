# Deploying Rasayana

A safe, free path to production, shaped the same way Amplitude and Worldsheet already
ship: a Vite app on Vercel, with one small serverless layer for anything that needs a
secret. Nothing here puts a key in the repo, and nothing here costs money.

## Launch plan (decided 2026-06-14): Vercel + Neon, free

The stack is chosen and the wiring is built and validated locally: **Vercel** serves the
static frontend at `rasayana.vayuai.ai` and runs the API as a **Python serverless
function** (`api/index.py` mounts the FastAPI app under `/api`), reading a free **Neon**
Postgres. The four deploy artifacts are committed: `vercel.json`, `api/index.py`,
`requirements.txt` (lean runtime deps), `.vercelignore`. I booted `api/index.py` locally
and confirmed `/api/stats`, `/api/common-ailments`, `/api/plant-index`, and the `/api/chat`
SSE stream all answer.

**Two things from you, then I take it live:**

1. **Log in to Vercel:** run `vercel login` in a terminal (or tell me the account/team).
2. **Create a free Neon project** at neon.tech and paste its connection string into a local
   file `.env.deploy` (gitignored, never committed):
   `NEON_DATABASE_URL=postgresql://USER:PASS@ep-xxx-pooler.REGION.aws.neon.tech/neondb?sslmode=require`
   (use the **pooled** string, the host with `-pooler`, it suits serverless).

**Then I run, from your machine:**

- `bash scripts/load_neon.sh` to dump the local graph and restore it into Neon (79 MB
  dump, fits the free 512 MB tier), and create the select-only `vayu_ro` role.
- Set the Vercel env vars (no secret ever printed or committed): `DATABASE_URL` (the Neon
  URL with the `postgresql+psycopg://` prefix), optional `DATABASE_URL_RO` (the `vayu_ro`
  role), and the LLM keys copied from your local `.env` (`CEREBRAS_API_KEY`, etc.).
- `vercel --prod` to build and deploy, then attach `rasayana.vayuai.ai` (your A record is
  already pointed at Vercel), then smoke-test every surface live.

The rest of this document is the background and the alternative paths.

## TL;DR

1. **Frontend**: `web/` is a static Vite build. Vercel serves it for free.
2. **Data**: load the knowledge graph into a free hosted Postgres (your existing Supabase
   project, or a new Neon database). The local 454 MB database fits inside the 512 MB free
   tier with a little trimming.
3. **API and Ask**: deploy the FastAPI backend as a Vercel serverless function pointed at
   that database. The LLM keys and the database URL live in Vercel environment variables,
   the same place Amplitude keeps its tutor key. They never touch git.

Serverless scales to zero, so an idle site costs nothing and there is no always-on server
to attack.

## Why not just publish the current backend

Today the app runs on a 454 MB local Postgres behind FastAPI. That is ideal for building,
but to publish it as-is you would need an always-on database and a public API. That is:

- larger than any free always-on tier,
- a surface you would have to secure, patch, and monitor,
- slow on free tiers, which suspend idle services and cold-start them.

None of it is necessary. The site is read-only, the database role it uses (`vayu_ro`)
cannot write, and serverless functions give you the same endpoints without a server you
have to babysit.

## Two paths

| | Path A, full tool (recommended) | Path B, leanest |
|---|---|---|
| Browse the library | Yes | Yes |
| The interactive course | Yes | Yes |
| Wikipedia overviews | Yes, client side | Yes, client side |
| Natural-language Ask | Yes | No, or guided presets only |
| Backend | One Vercel serverless function | None |
| Database | Free Postgres (Supabase or Neon) | Static JSON bundled in the build |
| Cost | Free | Free |
| Secrets | In Vercel env only | None |
| Best when | You want the real tool live | You want the simplest possible page |

Path A keeps the product whole and is still free and safe, so it is the recommendation.
Path B is the fallback if you ever want a zero-backend page and can live without free-text
Ask.

## Path A, step by step

Everything below is free. None of it commits a secret.

### 1. Put the graph in a free Postgres
Use the Supabase project you already have, or create a Neon database (both give a 512 MB
free tier). Dump the local database and load it:

```bash
# from this repo, with the local db running
pg_dump --no-owner --no-privileges vayu > vayu.dump
# load into the hosted database (paste its connection string when prompted, do not commit it)
psql "<HOSTED_DATABASE_URL>" < vayu.dump
```

The full database is about 454 MB. If it runs tight against the 512 MB cap, the
InChIKey-only "unnamed compound" rows are the easy thing to drop, they are already hidden
in the UI. I can write that trim as a one-line migration when you are ready.

Recreate the read-only role on the hosted database so the API and Ask cannot write:

```sql
create role vayu_ro nologin;
grant connect on database postgres to vayu_ro;
grant usage on schema public to vayu_ro;
grant select on all tables in schema public to vayu_ro;
```

### 2. Deploy the frontend and API on Vercel
- Import the GitHub repo into Vercel.
- Set the project root to `web/` and let it auto-detect Vite. Build command `npm run build`,
  output `dist`.
- Add the FastAPI app (`vayu/api`) as a Python serverless function, and add a rewrite so
  the frontend's `/api/*` calls reach it. I will add the `vercel.json` and the function
  entrypoint as part of wiring this up.

### 3. Set the secrets in Vercel, never in git
In the Vercel project settings, add environment variables:

- `DATABASE_URL`, the hosted Postgres connection string, using the `vayu_ro` role.
- The LLM provider keys the Ask feature falls back through (Cerebras, Mistral, Groq, NVIDIA,
  Gemini, OpenRouter). Add only the ones you want live; the chain skips any that are absent.

These mirror the `.env` you already use locally. The `.env` file stays gitignored and is
never deployed; Vercel injects its own copy at runtime.

### 4. Point the domain
You already have the GoDaddy A record for `rasayana` aimed at Vercel (`76.76.21.21`). Add
the domain in the Vercel project and it goes live on your own name.

## Security checklist, run before every deploy

- `.env` is gitignored and never committed. The repo is public.
- `data-and-keys/` lives outside the repo and is never committed or pasted into tracked files.
- No key value is ever written into a tracked file, including docs and examples.
- Secret scan of tracked files comes back clean (the build pipeline runs this before pushing).
- The database role the deployment uses is `vayu_ro`, select-only.

## Path B, the zero-backend fallback

If you ever want the simplest possible page: pre-export the browse lists and the most
visited detail pages to static JSON at build time, bundle them with the frontend, and ship
Ask either turned off or as a small set of guided, pre-answered queries. The library and
the course stay fully interactive; only free-text Ask goes away. No database, no function,
no secrets. Useful as a mirror or a lightweight launch, but Path A is the better home for
the real tool.

## When you are ready

Say "do Path A" and I will:

1. add the `vercel.json`, the serverless entrypoint, and the `/api` rewrite,
2. write the optional trim migration so the graph fits the free tier with headroom,
3. run the production build and hand you the exact `vercel` and `psql` commands to paste,
   so the only thing you ever type by hand is the secret values, straight into Vercel.
