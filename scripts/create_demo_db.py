#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mosaic_demo.db import connect, init_db
from mosaic_demo.seed import seed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/mosaic_demo.sqlite3")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if args.fresh and db_path.exists():
        db_path.unlink()

    with connect(db_path) as conn:
        init_db(conn)
        existing = conn.execute("SELECT COUNT(*) AS count FROM service_requests").fetchone()
        if existing["count"] == 0:
            seed(conn)

    print(f"Demo database ready: {db_path}")


if __name__ == "__main__":
    main()
