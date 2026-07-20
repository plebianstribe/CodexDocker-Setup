---
name: goal-creator
description: Create or update one active non-recursive goal scope with provable, testable subgoals and deterministic stage/evidence contracts.
---

# Goal Creator

Create decision-ready goal specs for execution and harsh gating.

## Crossreference Format
- All document crossreferences must use relative paths with `.md` extensions.
- Do not use absolute filesystem paths for crossreferences.
- Keep links portable so references remain valid if the repository is copied or moved.

## Scope Boundary
- Use this skill for one active non-recursive goal scope.
- If request implies recursive family structure (master/part/suffix), hand off to `recursive-goal-creator`.

## Required Inputs
1. User objective and constraints.
2. Existing `*_GOALS.md` and `*_COMPLETIONTRACKER.md` files (`*_COMPTRACKER.md` accepted as legacy alias).
3. `../contracts/goal_schema.md`.
4. `../contracts/stage_gate.md`.
5. `../contracts/evidence.md`.
6. `../goal-boundary-judge/SKILL.md` when boundary fit is uncertain.

## Naming Logic
- Single-scope mode only:
- `<GOAL_PREFIX>_GOALS.md`
- `<GOAL_PREFIX>_COMPLETIONTRACKER.md` (canonical)
- Use uppercase snake case for `<GOAL_PREFIX>`.

## Workflow
1. Normalize objective.
2. Draft subgoals with dependencies, acceptance criteria, and explicit evidence hooks.
3. Assign each subgoal `stage_id` in `*_GOALS.md` based on blocking/dependency order.
4. Build `*_COMPLETIONTRACKER.md` sorted by stage with parallel groups per stage.
5. Run/prepare boundary judge validation when scope fit is unclear.
6. Finalize completion tracker with deterministic unlock conditions and blocker handling.

## Output Contract
1. `Objective`
2. `Active Goal Scope`
3. `Reuse Decision`
4. `Subgoal Plan`
5. `Stage Assignments (in GOALS)`
6. `Completion Tracker (Stage-Sorted)`
7. `Evidence Requirements`
8. `Open Risks`
