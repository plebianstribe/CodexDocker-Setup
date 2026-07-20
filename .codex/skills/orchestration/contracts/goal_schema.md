# Goal Schema Contract

Use this contract to keep goal-family documents deterministic for downstream execution and gating.

## Standard Pair Files
- `<GOAL_PREFIX>_GOALS.md`
- `<GOAL_PREFIX>_COMPLETIONTRACKER.md` (canonical)

## Recursive Family Files
- `<PREFIX>_MASTER.md`
- `<PREFIX>_COMPLETIONTRACKER.md` (canonical)
- one or more family `*_GOALS.md` files (`PART{i}` or `<SUFFIX>` variants)

Legacy compatibility:
- If `*_COMPTRACKER.md` exists, treat it as the same role as `*_COMPLETIONTRACKER.md`.
- For new files, always write `COMPLETIONTRACKER` spelling.

## Required Step Fields (`*_GOALS.md`)
Each step must include:
- `step_id`
- `title`
- `status` (`pending|in_progress|blocked|completed`)
- `stage_id` (single assigned stage, based on blocking/dependency order)
- `depends_on` (step IDs)
- `acceptance_criteria` (testable statements)
- `expected_outputs` (artifact paths or structured outputs)
- `expected_functional_change` (user-visible or architectural)
- `required_tests` (unit/integration/e2e names or commands)
- `evidence` (filled during execution)

## Stage Assignment Rules (`*_GOALS.md`)
- Assign every step to exactly one `stage_id`.
- Place dependency-blocked steps in later stages than their blocking prerequisites.
- Allow same-stage placement only when dependencies are non-blocking and parallel-safe.

## Consistency Rules
- Every step in goals docs appears in the completion tracker stage map.
- `stage_id` in goals docs matches the completion tracker assignment.
- Completion tracker sections are sorted by stage order.
- Completion tracker never references unknown step IDs.
- Unlock conditions reference concrete step IDs and evidence expectations.
- No duplicate step IDs across a recursive family.
