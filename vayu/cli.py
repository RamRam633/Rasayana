"""Vayu CLI.  `vayu <cmd>` (installed) or `python -m vayu.cli <cmd>`."""
from __future__ import annotations

import argparse
import json
import sys

from vayu import db
from vayu.etl.pipeline import list_sources, run_ingest


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="vayu", description="Vayu Materia ETL & ops")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("healthcheck", help="check DB connectivity")
    sub.add_parser("sources", help="list registered source extractors")
    sub.add_parser("seed-demo", help="load the curated demo dataset (live GBIF + PubChem)")

    ing = sub.add_parser("ingest", help="run a source extractor -> normalize -> load")
    ing.add_argument("source", help="source short_code (e.g. pubchem, imppat, duke)")
    ing.add_argument("--name", help="single-entity probe, e.g. a compound name for pubchem")
    ing.add_argument("--limit", type=int, default=None, help="cap records (dev)")
    ing.add_argument("--dry-run", action="store_true", help="extract+normalize, skip load")

    args = p.parse_args(argv)

    if args.cmd == "healthcheck":
        ok = db.healthcheck()
        print("db: ok" if ok else "db: FAIL")
        return 0 if ok else 1

    if args.cmd == "sources":
        print(json.dumps(list_sources(), indent=2))
        return 0

    if args.cmd == "seed-demo":
        from vayu.seed import seed_demo

        print(json.dumps(seed_demo(), indent=2))
        return 0

    if args.cmd == "ingest":
        result = run_ingest(args.source, name=args.name, limit=args.limit, dry_run=args.dry_run)
        print(json.dumps(result, indent=2, default=str))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
