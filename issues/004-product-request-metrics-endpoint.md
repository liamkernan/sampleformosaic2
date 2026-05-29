# P3: Add a lightweight queue metrics endpoint

## Request

The support lead wants a simple endpoint for a status dashboard:

```text
GET /metrics
```

It should return JSON with counts of open requests by priority and the oldest
open request timestamp:

```json
{
  "open_by_priority": {
    "urgent": 1,
    "high": 2,
    "normal": 4,
    "low": 1
  },
  "oldest_open_created_at": "2026-05-29T14:00:00+00:00"
}
```

## Acceptance Criteria

- Add unit tests for the metrics calculation.
- Add web handler coverage for `GET /metrics`.
- Keep the response stable when there are no open requests.

