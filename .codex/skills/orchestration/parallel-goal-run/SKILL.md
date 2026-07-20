---
name: parallel-goal-run
description: Execute active goal scopes with dependency-aware stage parallelism, including optional benchmark ablation mode under the same runner.
---

# PARALLEL-GOAL-RUN

Execute goal-directed implementation using staged parallelism and harsh gating.

## Crossreference Format
- All document crossreferences must use relative paths with `.md` extensions.
- Do not use absolute filesystem paths for crossreferences.
- Keep links portable so references remain valid if the repository is copied or moved.

## Required Inputs
1. Active goals scope files:
- standard mode: `<GOAL_PREFIX>_GOALS.md` and `<GOAL_PREFIX>_COMPLETIONTRACKER.md` (`<GOAL_PREFIX>_COMPTRACKER.md` legacy alias)
- recursive mode: family `*_GOALS.md`, `<PREFIX>_MASTER.md`, and `<PREFIX>_COMPLETIONTRACKER.md` (`<PREFIX>_COMPTRACKER.md` legacy alias)
2. `../contracts/goal_schema.md`.
3. `../contracts/stage_gate.md`.
4. `../contracts/evidence.md`.
5. `references/stage_run_template.md`.
6. Optional ablation inputs when `execution_mode = ablation`:
- benchmark ID and evaluation command contract
- optional `*_Components.md` inventory
- active report file (`<GoalPrefix>_Report.md` or equivalent)

## Execution Modes
- `standard`: normal stage-based implementation.
- `ablation`: benchmark matrix execution managed by this same runner.

## Active Scope Rule
- Update active goals file and active tracker context only.
- In recursive mode, read master + completion tracker for cross-goal dependency awareness.
- Do not modify unrelated goals files unless explicitly requested.

## Execution Workflow
1. Load steps from active goals file(s).
2. Load stage-sorted groups and unlock conditions from completion tracker.
3. Build runnable queue by dependencies, current stage, and non-conflicting files.
4. Execute same-stage non-conflicting work in parallel.
5. Run harsh gate after each completed step.
6. Update completion tracker status, evidence, and blockers.

## Ablation Workflow (execution_mode = ablation)
1. Filter ablation-relevant step IDs.
2. Build matrix: `{component_variant x benchmark_setting}`.
3. Route runnable cells into same-stage non-conflicting groups.
4. Execute cells, collect benchmark artifacts, and gate each completed cell.
5. Update report with top status summary and assumption/hypothesis resolution.

## Output Contract
1. `Active Goal Scope`
2. `Execution Mode`
3. `Current Stage`
4. `Runnable Steps (Parallel)`
5. `In-Progress/Blocked`
6. `Completed This Cycle`
7. `Artifacts Produced`
8. `Next Stage Unlock Condition (from completion tracker)`
9. `Cross-Goal Dependency Notes (recursive mode)`
10. `Ablation Summary` (ablation mode only)
