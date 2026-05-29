from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any


SLA_HOURS = {
    "urgent": 4,
    "high": 24,
    "normal": 72,
    "low": 168,
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def get_or_create_requester(
    conn: sqlite3.Connection,
    email: str,
    name: str = "",
) -> int:
    normalized = email.strip().lower()
    existing = conn.execute(
        "SELECT id FROM requesters WHERE email = ?",
        (normalized,),
    ).fetchone()
    if existing:
        return int(existing["id"])

    cursor = conn.execute(
        "INSERT INTO requesters (email, name) VALUES (?, ?)",
        (normalized, name.strip()),
    )
    return int(cursor.lastrowid)


def create_request(
    conn: sqlite3.Connection,
    *,
    source: str,
    requester_email: str,
    service: str,
    title: str,
    body: str,
    priority: str = "normal",
    external_ref: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    created = now or utc_now()
    priority_key = priority.strip().lower() or "normal"
    sla_due_at = created + timedelta(hours=SLA_HOURS.get(priority_key, SLA_HOURS["normal"]))
    requester_id = get_or_create_requester(conn, requester_email)

    cursor = conn.execute(
        """
        INSERT INTO service_requests (
            source, requester_id, service, title, body, status, priority,
            external_ref, created_at, updated_at, sla_due_at
        )
        VALUES (?, ?, ?, ?, ?, 'open', ?, ?, ?, ?, ?)
        """,
        (
            source.strip().lower(),
            requester_id,
            service.strip().lower(),
            title.strip(),
            body.strip(),
            priority_key,
            external_ref,
            iso(created),
            iso(created),
            iso(sla_due_at),
        ),
    )
    request_id = int(cursor.lastrowid)
    conn.execute(
        """
        INSERT INTO audit_events (request_id, actor, event_type, note, created_at)
        VALUES (?, 'system', 'created', ?, ?)
        """,
        (request_id, f"Created from {source}", iso(created)),
    )
    conn.commit()
    return get_request(conn, request_id)


def get_request(conn: sqlite3.Connection, request_id: int) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT
            sr.id,
            sr.source,
            r.email AS requester_email,
            r.name AS requester_name,
            sr.service,
            sr.title,
            sr.body,
            sr.status,
            sr.priority,
            sr.external_ref,
            sr.created_at,
            sr.updated_at,
            sr.sla_due_at
        FROM service_requests sr
        JOIN requesters r ON r.id = sr.requester_id
        WHERE sr.id = ?
        """,
        (request_id,),
    ).fetchone()
    if row is None:
        raise KeyError(f"request {request_id} not found")
    return row_to_dict(row)


def list_requests(
    conn: sqlite3.Connection,
    *,
    status: str | None = None,
    source: str | None = None,
    service: str | None = None,
    sort: str = "created",
) -> list[dict[str, Any]]:
    clauses: list[str] = []
    params: list[str] = []
    if status:
        clauses.append("sr.status = ?")
        params.append(status.strip().lower())
    if source:
        clauses.append("sr.source = ?")
        params.append(source.strip().lower())
    if service:
        clauses.append("sr.service = ?")
        params.append(service.strip().lower())

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    order_by = "sr.created_at DESC"
    if sort == "sla":
        order_by = "sr.created_at ASC"
    elif sort == "priority":
        order_by = """
        CASE sr.priority
            WHEN 'urgent' THEN 0
            WHEN 'high' THEN 1
            WHEN 'normal' THEN 2
            ELSE 3
        END,
        sr.created_at ASC
        """

    rows = conn.execute(
        f"""
        SELECT
            sr.id,
            sr.source,
            r.email AS requester_email,
            sr.service,
            sr.title,
            sr.status,
            sr.priority,
            sr.external_ref,
            sr.created_at,
            sr.updated_at,
            sr.sla_due_at
        FROM service_requests sr
        JOIN requesters r ON r.id = sr.requester_id
        {where}
        ORDER BY {order_by}
        """,
        params,
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def close_request(
    conn: sqlite3.Connection,
    request_id: int,
    *,
    actor: str = "mosaic",
    note: str = "",
    now: datetime | None = None,
) -> dict[str, Any]:
    closed_at = now or utc_now()
    current = get_request(conn, request_id)
    if current["status"] == "closed":
        return current

    conn.execute(
        """
        UPDATE service_requests
        SET status = 'closed', updated_at = ?
        WHERE id = ?
        """,
        (iso(closed_at), request_id),
    )
    conn.execute(
        """
        INSERT INTO audit_events (request_id, actor, event_type, note, created_at)
        VALUES (?, ?, 'updated', ?, ?)
        """,
        (request_id, actor, note, iso(closed_at)),
    )
    conn.commit()
    return get_request(conn, request_id)


def audit_log(conn: sqlite3.Connection, request_id: int) -> list[dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT id, request_id, actor, event_type, note, created_at
        FROM audit_events
        WHERE request_id = ?
        ORDER BY created_at ASC, id ASC
        """,
        (request_id,),
    ).fetchall()
    return [row_to_dict(row) for row in rows]

