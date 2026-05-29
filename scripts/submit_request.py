#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mosaic_demo.db import connect
from mosaic_demo.service import create_request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="data/mosaic_demo.sqlite3")
    parser.add_argument("--source", required=True)
    parser.add_argument("--requester-email", required=True)
    parser.add_argument("--service", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--priority", default="normal")
    parser.add_argument("--external-ref")
    args = parser.parse_args()

    with connect(args.db) as conn:
        created = create_request(
            conn,
            source=args.source,
            requester_email=args.requester_email,
            service=args.service,
            title=args.title,
            body=args.body,
            priority=args.priority,
            external_ref=args.external_ref,
        )
    print(f"Created request #{created['id']}: {created['title']}")


if __name__ == "__main__":
    main()
