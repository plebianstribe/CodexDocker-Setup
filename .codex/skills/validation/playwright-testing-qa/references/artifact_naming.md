# Artifact Naming

Write artifacts under `artifacts/ui/<run_id>/` using deterministic names.

Use `<scenario>` slug for each test flow.

- Screenshots:
- `screenshots/<scenario>_initial.png`
- `screenshots/<scenario>_in_progress.png`
- `screenshots/<scenario>_complete_marked.png`
- `screenshots/<scenario>_verification_target.png`
- Trace:
- `traces/<scenario>_trace.zip`
- Action log:
- `logs/<scenario>_action_log.json`
- Capture summary:
- `playwright_capture_<scenario>_report.json`

Video files are recorded to `videos/` using Playwright default names.
