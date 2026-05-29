from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from mosaic_demo.db import connect, init_db
from mosaic_demo.service import create_request, list_requests


class SlaSortReportedIssueTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "demo.sqlite3"
        self.conn = connect(self.db_path)
        init_db(self.conn)

    def tearDown(self) -> None:
        self.conn.close()
        self.tmpdir.cleanup()

    def test_sla_sort_orders_by_due_at_not_created_at(self) -> None:
        create_request(
            self.conn,
            source="email",
            requester_email="ops@example.com",
            service="billing",
            title="Old low priority cleanup",
            body="Clean up stale labels.",
            priority="low",
            external_ref="email:old-low",
            now=datetime(2026, 5, 1, 12, tzinfo=timezone.utc),
        )
        urgent = create_request(
            self.conn,
            source="slack",
            requester_email="finance@example.com",
            service="billing",
            title="Invoice export is blocking close",
            body="Finance cannot finish month-end close.",
            priority="urgent",
            external_ref="slack:new-urgent",
            now=datetime(2026, 5, 2, 12, tzinfo=timezone.utc),
        )

        queue = list_requests(self.conn, status="open", sort="sla")

        self.assertEqual(urgent["id"], queue[0]["id"])


if __name__ == "__main__":
    unittest.main()

