# Harsh Gate Checklist

Use this checklist for each completed step in the active goal pair.

## A) Functionality Gate
- Acceptance criteria in active goals file are testably satisfied.
- Required unit/integration/e2e tests pass.
- Expected outputs exist at declared paths or match declared payload contracts.
- Expected functional or architectural change is evidenced.

## B) Stage/Tracker Gate
- Step is mapped to a valid stage in active completion tracker.
- Tracker dependencies for the step are satisfied.
- Unlock conditions for next stage are either satisfied or explicitly blocked with reason.

## C) QA Gate
- If UI-impacting, evidence includes deterministic QA artifacts (screenshots/logs/trace/video where applicable).
- If model/training-impacting, run `model-validation-qa` small-subset validation before full experiments.
- Artifact naming and timing policies pass where applicable.

## D) Governance Gate
- Scope remains inside active objective boundaries.
- No hidden scope expansion in unrelated modules.
- Risk notes and mitigations are documented for blockers.

## Verdict Rules
- PASS: all gates pass.
- CONDITIONAL PASS: core functionality and safety pass; only non-critical debt remains.
- FAIL: any functionality/safety/contract gate fails.
