# Wait Timing Policy

- Minimum delay between clicks is at least `0.5s`.
- Default delay for this repository is `0.7s` (`700ms`).
- Store click timestamps and `delta_from_previous_ms` in the action log.
- If the provided delay argument is below `500`, fail fast with an error.
- Log `raw_delta_before_wait_ms` and `wait_applied_ms` for auditable pacing.
