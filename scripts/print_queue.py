#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mosaic_demo.db import connect
from mosaic_demo.service import list_requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/mosaic_demo.sqlite3")
    parser.add_argument("--status", default="open")
    parser.add_argument("--sort", default="created")
    args = parser.parse_args()

    with connect(args.db) as conn:
        for item in list_requests(conn, status=args.status, sort=args.sort):
            print(
                f"#{item['id']} {item['priority']:7} {item['sla_due_at']} "
                f"{item['service']:10} {item['title']}"
            )


if __name__ == "__main__":
    main()
