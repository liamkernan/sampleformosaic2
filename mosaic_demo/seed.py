from __future__ import annotations

from datetime import datetime, timezone

from .service import create_request


def seed(conn) -> None:
    examples = [
        (
            datetime(2026, 5, 20, 14, 0, tzinfo=timezone.utc),
            {
                "source": "slack",
                "requester_email": "lee.data@example.com",
                "service": "analytics",
                "title": "Daily active users chart shows local time as UTC",
                "body": "The dashboard label says UTC, but the values appear to be Eastern Time.",
                "priority": "low",
                "external_ref": "slack:C222:1770000000.000002",
            },
        ),
        (
            datetime(2026, 5, 29, 14, 0, tzinfo=timezone.utc),
            {
                "source": "slack",
                "requester_email": "nora.ops@example.com",
                "service": "billing",
                "title": "Invoice export drops EU VAT IDs",
                "body": "Finance cannot reconcile EU invoices because exported rows have blank VAT IDs.",
                "priority": "urgent",
                "external_ref": "slack:C111:1770000000.000001",
            },
        ),
        {
            "source": "email",
            "requester_email": "sam.support@example.com",
            "service": "accounts",
            "title": "Password reset page accepts expired token",
            "body": "A customer opened a 3-day-old reset email and still reached the password form.",
            "priority": "high",
            "external_ref": "email:msg-1001",
        },
        {
            "source": "web",
            "requester_email": "maya.pm@example.com",
            "service": "catalog",
            "title": "Add CSV export for filtered product list",
            "body": "Merchandising wants a CSV export button that preserves active filters.",
            "priority": "normal",
            "external_ref": "web:REQ-2026-018",
        },
    ]
    default_time = datetime(2026, 5, 29, 15, 0, tzinfo=timezone.utc)
    for offset, example in enumerate(examples):
        if isinstance(example, tuple):
            created_at, payload = example
        else:
            created_at, payload = default_time.replace(hour=default_time.hour + offset), example
        create_request(conn, now=created_at, **payload)
