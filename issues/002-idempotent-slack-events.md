# P1: Retried Slack events create duplicate support requests

## Report

Slack retries webhook delivery when it does not receive a fast response. When
that happens, Mosaic should treat the same `source` plus `external_ref` as the
same intake event. The current app creates duplicate open requests.

## Expected

If `create_request` receives the same non-empty `source` and `external_ref`, it
should update the existing request instead of inserting a new one. New title,
body, priority, service, and requester values should be reflected on the
existing row.

## Reproduction

```bash
python3 -m unittest tests.reported.test_002_idempotent_external_ref
```

## Notes for Mosaic

This should work for Slack, email, and web form sources. Empty or missing
`external_ref` values should still create distinct requests.

