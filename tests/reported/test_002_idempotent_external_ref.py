from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mosaic_demo.db import connect, init_db
from mosaic_demo.service import create_request, list_requests


class IdempotentExternalRefReportedIssueTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "demo.sqlite3"
        self.conn = connect(self.db_path)
        init_db(self.conn)

    def tearDown(self) -> None:
        self.conn.close()
        self.tmpdir.cleanup()

    def test_duplicate_source_external_ref_updates_existing_request(self) -> None:
        first = create_request(
            self.conn,
            source="slack",
            requester_email="ops@example.com",
            service="accounts",
            title="Password reset token expires too late",
            body="Original report.",
            priority="high",
            external_ref="slack:C123:1770000000.000001",
        )
        second = create_request(
            self.conn,
            source="slack",
            requester_email="ops@example.com",
            service="accounts",
            title="Password reset token expires too late",
            body="Original report plus screenshot.",
            priority="urgent",
            external_ref="slack:C123:1770000000.000001",
        )

        items = list_requests(self.conn, status="open", source="slack")

        self.assertEqual(first["id"], second["id"])
        self.assertEqual(1, len(items))
        self.assertEqual("urgent", items[0]["priority"])
        self.assertIn("screenshot", items[0]["body"])


if __name__ == "__main__":
    unittest.main()

