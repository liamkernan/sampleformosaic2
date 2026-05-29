from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .db import connect, init_db
from .service import close_request, create_request, get_request, list_requests


DEFAULT_DB = Path("data/mosaic_demo.sqlite3")


class DemoHandler(BaseHTTPRequestHandler):
    db_path = DEFAULT_DB

    def send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            with connect(self.db_path) as conn:
                if parsed.path == "/health":
                    self.send_json(200, {"ok": True, "service": "mosaic-demo"})
                    return
                if parsed.path == "/requests":
                    query = parse_qs(parsed.query)
                    requests = list_requests(
                        conn,
                        status=_one(query, "status"),
                        source=_one(query, "source"),
                        service=_one(query, "service"),
                        sort=_one(query, "sort") or "created",
                    )
                    self.send_json(200, {"requests": requests})
                    return
                if parsed.path.startswith("/requests/"):
                    request_id = int(parsed.path.split("/")[2])
                    self.send_json(200, get_request(conn, request_id))
                    return
        except KeyError as exc:
            self.send_json(404, {"error": str(exc)})
            return
        except Exception as exc:
            self.send_json(500, {"error": str(exc)})
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self.read_json()
            with connect(self.db_path) as conn:
                if parsed.path == "/requests":
                    created = create_request(conn, **payload)
                    self.send_json(201, created)
                    return
                if parsed.path.startswith("/requests/") and parsed.path.endswith("/close"):
                    request_id = int(parsed.path.split("/")[2])
                    closed = close_request(
                        conn,
                        request_id,
                        actor=payload.get("actor", "mosaic"),
                        note=payload.get("note", ""),
                    )
                    self.send_json(200, closed)
                    return
        except KeyError as exc:
            self.send_json(404, {"error": str(exc)})
            return
        except Exception as exc:
            self.send_json(400, {"error": str(exc)})
            return
        self.send_json(404, {"error": "not found"})


def _one(query: dict[str, list[str]], key: str) -> str | None:
    values = query.get(key)
    return values[0] if values else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(db_path) as conn:
        init_db(conn)

    DemoHandler.db_path = db_path
    server = ThreadingHTTPServer((args.host, args.port), DemoHandler)
    print(f"Serving mosaic demo on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

