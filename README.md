# Mosaic Demo Service

This repository is a new local playground for testing Mosaic against a realistic
database-backed service. The app models a small support intake system where
requests arrive from Slack, email, or a web form, are triaged, and then closed
after a fix is shipped.

The project intentionally includes a few realistic bugs and product requests in
`issues/`. Use those issue files as prompts for Mosaic. The smoke tests describe
current working behavior; the reported tests reproduce the backlog items and
will fail until Mosaic implements the corresponding fix.

## Quick Start

```bash
python3 scripts/create_demo_db.py
python3 -m unittest discover tests/smoke
python3 -m mosaic_demo.web --db data/mosaic_demo.sqlite3 --port 8000
```

Then open:

```text
http://localhost:8000/health
http://localhost:8000/requests?status=open
http://localhost:8000/requests?status=open&sort=sla
```

## Testing Mosaic

1. Pick one file in `issues/`.
2. Submit it to Mosaic as a user request.
3. Let Mosaic inspect the repo, add or update tests, and open a pull request.
4. Verify with the related command from the issue file.

Useful commands:

```bash
python3 -m unittest discover tests/smoke
python3 -m unittest discover tests/reported
python3 scripts/create_demo_db.py --fresh
python3 scripts/print_queue.py --sort sla
```

## Project Layout

```text
mosaic_demo/          app code
scripts/              setup and inspection helpers
tests/smoke/          passing baseline tests
tests/reported/       failing reproductions for Mosaic to fix
issues/               realistic support/change requests
data/                 generated SQLite database location
```

## API

`GET /health`

Returns basic service status.

`GET /requests?status=open&sort=sla`

Lists service requests. Supported filters are `status`, `source`, `service`,
and `sort`.

`POST /requests`

Creates a service request from JSON:

```json
{
  "source": "slack",
  "requester_email": "ada@example.com",
  "service": "billing",
  "title": "Invoice export is missing tax IDs",
  "body": "The finance team cannot reconcile May invoices.",
  "priority": "high",
  "external_ref": "slack:T123:1748451600.000"
}
```

`POST /requests/{id}/close`

Closes a request with optional JSON:

```json
{
  "actor": "mosaic",
  "note": "Fixed in PR #42"
}
```
