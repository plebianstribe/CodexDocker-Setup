---
name: goal-harsh-judge
description: Run strict functional and QA acceptability gates for completed goal steps using objective evidence and deterministic stage unlock rules.
---

# Goal Harsh Judge

## Crossreference Format
- All document crossreferences must use relative paths with `.md` extensions.
- Do not use absolute filesystem paths for crossreferences.
- Keep links portable so references remain valid if the repository is copied or moved.

## Required Inputs
1. Active `*_GOALS.md`.
2. Active tracker:
- standard mode: matching `*_COMPLETIONTRACKER.md` (`*_COMPTRACKER.md` legacy alias)
- recursive mode: unified `<PREFIX>_COMPLETIONTRACKER.md` (`<PREFIX>_COMPTRACKER.md` legacy alias)
3. `references/harsh_gate_checklist.md`.
4. `../contracts/goal_schema.md`.
5. `../contracts/stage_gate.md`.
6. `../contracts/evidence.md`.
7. Latest user-reported runtime signal (if provided), treated as advisory unless supported by objective evidence artifacts.

## Workflow
1. Identify completed step ID.
2. Validate evidence against acceptance criteria, outputs, functional change, and required tests.
3. Validate stage unlock rules from the active tracker.
4. Reconcile live user-verified signals:
- user-reported live failure is blocker input and must be resolved before PASS.
- user-reported live PASS is supplemental only (never standalone PASS evidence).
5. Issue `PASS`, `CONDITIONAL PASS`, or `FAIL`.

## Output Contract
1. `Step Audited`
2. `Active Goal Scope`
3. `Evidence Run Id`
4. `Harsh Verdict`
5. `Blocking Findings`
6. `Non-Blocking Findings`
7. `Stage Unlock Decision (from completion tracker)`
8. `Required Fixes Before Next Stage`
