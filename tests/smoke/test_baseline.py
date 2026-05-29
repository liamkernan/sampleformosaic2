from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mosaic_demo.db import connect, init_db
from mosaic_demo.seed import seed
from mosaic_demo.service import audit_log, close_request, create_request, list_requests


class BaselineBehaviorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "demo.sqlite3"
        self.conn = connect(self.db_path)
        init_db(self.conn)

    def tearDown(self) -> None:
        self.conn.close()
        self.tmpdir.cleanup()

    def test_create_and_list_request(self) -> None:
        created = create_request(
            self.conn,
            source="web",
            requester_email="Casey@example.com",
            service="catalog",
            title="Import status is confusing",
            body="The import page says done before validation finishes.",
            priority="high",
            external_ref="web:123",
        )

        self.assertEqual(created["requester_email"], "casey@example.com")
        items = list_requests(self.conn, status="open", service="catalog")
        self.assertEqual([created["id"]], [item["id"] for item in items])

    def test_seed_data_has_open_requests(self) -> None:
        seed(self.conn)
        items = list_requests(self.conn, status="open")
        self.assertEqual(4, len(items))

    def test_close_request(self) -> None:
        created = create_request(
            self.conn,
            source="email",
            requester_email="sam@example.com",
            service="accounts",
            title="Reset copy needs update",
            body="The email still refers to the old help center.",
        )
        closed = close_request(self.conn, created["id"], note="Fixed copy")

        self.assertEqual("closed", closed["status"])
        self.assertEqual(2, len(audit_log(self.conn, created["id"])))


if __name__ == "__main__":
    unittest.main()

