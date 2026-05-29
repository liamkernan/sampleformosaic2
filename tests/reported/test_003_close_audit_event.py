from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mosaic_demo.db import connect, init_db
from mosaic_demo.service import audit_log, close_request, create_request


class CloseAuditReportedIssueTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "demo.sqlite3"
        self.conn = connect(self.db_path)
        init_db(self.conn)

    def tearDown(self) -> None:
        self.conn.close()
        self.tmpdir.cleanup()

    def test_close_writes_closed_audit_event(self) -> None:
        created = create_request(
            self.conn,
            source="web",
            requester_email="pm@example.com",
            service="catalog",
            title="CSV export button needed",
            body="Need a filtered CSV export.",
        )

        close_request(self.conn, created["id"], actor="mosaic", note="Fixed in PR #42")
        events = audit_log(self.conn, created["id"])

        self.assertEqual("closed", events[-1]["event_type"])
        self.assertEqual("mosaic", events[-1]["actor"])
        self.assertEqual("Fixed in PR #42", events[-1]["note"])


if __name__ == "__main__":
    unittest.main()

