---
name: recursive-goal-creator
description: Compose and maintain one master supergoal with non-overlapping subgoal plans using shared contracts and explicit boundary-judge decisions.
---

# Recursive Goal Creator

Build deterministic recursive goal families compatible with staged execution and harsh gating.

## Crossreference Format
- All document crossreferences must use relative paths with `.md` extensions.
- Do not use absolute filesystem paths for crossreferences.
- Keep links portable so references remain valid if the repository is copied or moved.

## Required Inputs
1. User objective, constraints, and explicit out-of-scope requests.
2. Existing recursive family files:
- `*_GOALS.md`
- `*_MASTER.md`
- `*_COMPLETIONTRACKER.md` (`*_COMPTRACKER.md` legacy alias)
3. `../contracts/goal_schema.md`.
4. `../contracts/stage_gate.md`.
5. `../contracts/evidence.md`.
6. `../goal-boundary-judge/SKILL.md`.

## Unified Recursive Family Requirement
Every recursive family should resolve to exactly one canonical file of each type:
- `<PREFIX>_MASTER.md`
- `<PREFIX>_COMPLETIONTRACKER.md`

## Workflow
1. Derive supergoal prefix.
2. Detect overlap with existing supergoals.
3. If overlap is meaningful, require explicit user confirmation before updates.
4. Run boundary judge when update/create/breakdown/mergeup choice is unclear.
5. Apply deterministic naming:
- family files: `<PREFIX>_MASTER.md`, `<PREFIX>_COMPLETIONTRACKER.md`
- root goals: `<PREFIX>_GOALS.md`
- large splits: `<PREFIX>_PART1_GOALS.md`, `<PREFIX>_PART2_GOALS.md`, ...
- isolated components: `<PREFIX>_<SUFFIX>_GOALS.md`
6. Draft steps and dependencies across family docs and assign `stage_id` per subgoal in each goals file.
7. Finalize unified completion tracker sorted by stage, including parallel groups, unlocks, and cross-goal dependencies.

## Non-Duplication Checks
1. No duplicate step IDs across family goals docs.
2. Unified completion tracker references only existing steps.
3. Stage assignments in goals docs match the completion tracker stage map.
4. Record boundary and overlap audit in `<PREFIX>_MASTER.md`.

## Output Contract
1. `Objective`
2. `Supergoal Prefix`
3. `Master File`
4. `Goal Set`
5. `COMPLETIONTRACKER File`
6. `Reuse Decision`
7. `Cross-Reference Graph`
8. `Disambiguation Audit`
9. `Open Risks`
