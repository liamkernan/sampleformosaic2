# P1: Urgent tickets can be hidden behind older low-priority requests

## Report

The support queue is supposed to show the next SLA breach first when an
operator chooses `sort=sla`. Right now, an old low-priority ticket can appear
above a newer urgent ticket even though the urgent ticket is due much sooner.

## Expected

`list_requests(..., sort="sla")` and `GET /requests?status=open&sort=sla`
should order by `sla_due_at ASC`, then `created_at ASC`.

## Reproduction

```bash
python3 -m unittest tests.reported.test_001_sla_sort
```

## Notes for Mosaic

Keep the existing `priority` sort behavior. This request only concerns the
`sla` sort mode.

