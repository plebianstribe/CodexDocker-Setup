# Stage Gate Contract

## Tracker Requirements (`*_COMPLETIONTRACKER.md`)
Must include:
- Stage-sorted table mapping each `step_id` to `stage_id`.
- Stage dependency graph (`stage_id` -> prerequisites).
- Parallelization groups for same-stage non-conflicting steps.
- Per-stage unlock conditions.
- Current stage cursor and latest run ID.
- Blockers and mitigation notes.

Legacy compatibility:
- If only `*_COMPTRACKER.md` exists, treat it as the active completion tracker.

## Execution Gate Rules
- Execute only steps whose dependencies and stage prerequisites are satisfied.
- Select runnable work from the current stage's parallel groups in completion tracker order.
- Run the harsh gate on each completed step before unlock progression.
- Mark blocker reason and mitigation when a step cannot pass gate checks.
- Do not advance stage cursor unless all stage unlock conditions are objectively met.

## Recursive Notes
- `*_MASTER.md` may define cross-goal dependencies consumed by completion tracker.
- Active edits should stay scoped to selected goal + tracker unless explicitly requested.
