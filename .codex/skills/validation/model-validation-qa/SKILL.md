---
name: model-validation-qa
description: Validate functional or architectural model updates with a deterministic small test subset before full training or experiments. Use when a user requests pre-training QA, model-change validation, architecture regression checks, or end-to-end test gating for ML-related updates.
---

# Model Validation QA

Run focused, reproducible validation for model-impacting changes before full runs.

## Required Inputs
1. Target functional or architectural update description.
2. Training/evaluation dataset location and schema.
3. Existing unit/integration/e2e test commands.
4. Active goal pair files when operating under goal execution:
- `<GOAL_PREFIX>_GOALS.md`
- `<GOAL_PREFIX>_COMPTRACKER.md`

Read `references/subset_validation_contract.md` before execution.

## Workflow
1. Define validation scope from changed behavior and failure risks.
2. Build a small deterministic subset from the task dataset.
3. Run targeted unit tests for changed modules.
4. Run targeted integration/E2E checks proving end-to-end functional correctness.
5. Compare observed behavior against expected functional and architectural outcomes.
6. Produce go/no-go decision for full training/experiments.

## Output Contract
Return sections in this order:
1. `Validation Scope`
2. `Subset Definition`
3. `Tests Executed`
4. `Results`
5. `Blocking Regressions`
6. `Go/No-Go For Full Run`
7. `Required Fixes`

## Cross-Skill Contract
- Under staged execution, align evidence and step ids with `parallel-goal-run` and `goal-harsh-judge` requirements.
- Use expected outputs and required tests defined by `goal-creator` goal specs.
