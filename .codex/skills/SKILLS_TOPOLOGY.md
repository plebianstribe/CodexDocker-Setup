# Skills Topology

This folder is organized into functional lanes to reduce overlap and make handoffs explicit.

## Lanes
- `.system/`: platform-managed baseline skills (imagegen, OpenAI docs, plugin/skill tooling).
- `orchestration/`: planning, goal creation, boundary decisions, staged execution, and harsh gating.
- `validation/`: UI/model/dependency validation workflows and test setup contracts.
- `strategy/`: domain/persona refinement and web-based market/SOTA verification.
- `platform/`: reserved for non-system platform extensions.

## Primary Handoffs
1. `orchestration/interactive-planner` -> `strategy/idea-domain-refiner` when persona/expertise refinement is requested.
2. `strategy/idea-domain-refiner` -> `strategy/web-sota-verifier` when external evidence is required.
3. `orchestration/goal-creator`/`recursive-goal-creator` -> `orchestration/parallel-goal-run` for execution.
4. `orchestration/parallel-goal-run` -> `orchestration/goal-harsh-judge` for gate verdicts.
5. `orchestration/goal-boundary-judge` controls `update|create|breakdown|mergeup` decisions.

## Shared Contracts
`orchestration/contracts/` is the single source of truth for goal schema, stage gating, and evidence.
