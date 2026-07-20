# Evidence Contract

Objective evidence is required for all PASS and stage unlock decisions.

## Minimum Evidence by Step
- command(s) executed
- status (pass/fail)
- artifact references (logs, screenshots, traces, reports)
- mapping back to `step_id` and acceptance criteria

## Domain-Specific Evidence Extensions
- UI-impacting changes: deterministic QA artifacts and action logs where applicable.
- Model/training-impacting changes: deterministic subset validation before full experiments.
- Dependency changes: manifest diff + installation verification + at least one successful target workflow command.

## Live User Signal Handling
- User-reported live failures are blocker input and require remediation evidence.
- User-reported live PASS signals are supplemental only and cannot replace objective evidence.
