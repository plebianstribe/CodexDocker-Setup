---
name: goal-boundary-judge
description: "Evaluate goal scope fitness and recursive-family boundaries, then choose exactly one action: update, create, breakdown, or mergeup."
---

# Goal Boundary Judge

Run one deterministic boundary decision pass for standard or recursive goal families.

## Crossreference Format
- All document crossreferences must use relative paths with `.md` extensions.
- Do not use absolute filesystem paths for crossreferences.
- Keep links portable so references remain valid if the repository is copied or moved.

## Scope Boundary
- This skill replaces both legacy `goal-creator-judge` and `recursive-goal-judge` behavior.
- Emit exactly one boundary action: `update`, `create`, `breakdown`, or `mergeup`.

## Required Inputs
1. User objective and requested change.
2. Active scope documents:
- standard mode: `*_GOALS.md` and matching `*_COMPLETIONTRACKER.md` (`*_COMPTRACKER.md` legacy alias)
- recursive mode: `*_MASTER.md`, `*_COMPLETIONTRACKER.md` (`*_COMPTRACKER.md` legacy alias), and family `*_GOALS.md` files
3. `references/boundary_judge_checklist.md`.
4. `../contracts/goal_schema.md`.
5. `../contracts/stage_gate.md`.
6. Latest user-request delta list (new blockers, verification claims, required scope additions).

## Workflow
1. Parse active steps, stage map, dependencies, and blockers.
2. Apply sprint-fit and quality checks (`2/5/10` day heuristic).
3. Compute complexity delta (`minimal|acceptable|overgrown`) for new requirements.
4. Evaluate overlap, duplication risk, and dependency coupling.
5. Select exactly one action:
- `update`: existing scope should absorb request.
- `create`: new goal family/scope is cleaner than extending current one.
- `breakdown`: current scope is overgrown and must split.
- `mergeup`: current scopes are too fragmented and should compact.
6. If decision confidence is low, request explicit user confirmation before any file edits.

## Output Contract
1. `Objective`
2. `Candidate Scopes`
3. `Sprint-Fit Assessment (2/5/10 days)`
4. `Complexity Delta Verdict` (`minimal|acceptable|overgrown`)
5. `Boundary Decision (update/create/breakdown/mergeup)`
6. `Decision Rationale`
7. `Required Fixes`
8. `Requested User Confirmation (if required)`
9. `Planned File Actions`
10. `Open Risks`
