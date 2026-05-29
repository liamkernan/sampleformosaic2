# P2: Closing a request writes the wrong audit event type

## Report

When Mosaic closes a request after opening a PR, the audit timeline shows a
generic `updated` event. Support operators want a specific `closed` event so
they can report on cycle time without parsing notes.

## Expected

`close_request` should append an audit event with `event_type = "closed"` and
preserve the actor and note.

## Reproduction

```bash
python3 -m unittest tests.reported.test_003_close_audit_event
```

