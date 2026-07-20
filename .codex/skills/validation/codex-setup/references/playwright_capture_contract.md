# Contract: Playwright Capture

## Purpose
Standardize UI capture settings for debugging and review.

## Required Inputs
- Test run ID.
- Target spec(s).
- Capture mode (`on-failure` or `always`).

## Expected Outputs
- Screenshots/traces/videos stored with deterministic names and paths.

## Command Patterns
- Screenshot path: `artifacts/ui/<run_id>/screenshots/`
- Trace path: `artifacts/ui/<run_id>/traces/`
- Video path: `artifacts/ui/<run_id>/videos/`

## Pass/Fail Criteria
- Pass: required captures exist for configured mode and are readable.
- Fail: missing/unreadable capture files or inconsistent naming.

## Artifact Locations
- UI artifacts: `/app/artifacts/ui/<run_id>/`

## Reuse Boundaries
- Shared capture contract for all UI-oriented validation steps.
- Visual approval workflow policies are out of scope.
