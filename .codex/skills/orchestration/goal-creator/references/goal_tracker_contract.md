# Goal and Completion Tracker Contract

Use this contract to keep goal files deterministic for downstream execution and judging.

## 1) `<GOAL_PREFIX>_GOALS.md`
Each step must include:
- `step_id`
- `title`
- `status` (`pending|in_progress|blocked|completed`)
- `stage_id` (single assigned stage by blocking/dependency order)
- `depends_on` (step ids)
- `acceptance_criteria` (testable statements)
- `expected_outputs` (artifact paths or structured outputs)
- `expected_functional_change` (user-visible or architectural)
- `required_tests` (unit/integration/e2e names or commands)
- `evidence` (filled during execution)

## 2) `<GOAL_PREFIX>_COMPLETIONTRACKER.md`
Must include:
- Stage-sorted table mapping each `step_id` to a `stage_id`.
- Stage dependency graph (`stage_id` -> prerequisites).
- Parallelization groups for same-stage non-conflicting steps.
- Per-stage unlock conditions.
- Current stage cursor and latest run id.
- Blockers and mitigation notes.

Legacy compatibility:
- `*_COMPTRACKER.md` is accepted as a legacy alias.

## 3) Consistency Rules
- Every step in goals file must appear in completion tracker stage map.
- Step `stage_id` in goals file must match completion tracker assignment.
- Completion tracker must not reference unknown `step_id`.
- Unlock conditions must reference concrete step ids and evidence expectations.
- Keep canonical naming exact: `<GOAL_PREFIX>_GOALS.md` and `<GOAL_PREFIX>_COMPLETIONTRACKER.md`.
