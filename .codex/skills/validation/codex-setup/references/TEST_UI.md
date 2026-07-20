# Skill: UI Test Execution

## Purpose
Define reusable UI test execution with deterministic capture and reporting.

## Required Inputs
- UI automation framework configuration (Playwright preferred).
- Target route/page scope.
- Capture contract for screenshots/traces.

## Expected Outputs
- UI test pass/fail result.
- Screenshot/trace/video artifacts following contract paths.

## Command Patterns
- `npx playwright test`
- `npx playwright test --grep <scenario>`
- `npx playwright show-report`

## Pass/Fail Criteria
- Pass: all targeted UI specs pass and required capture artifacts exist.
- Fail: any UI spec failure, missing capture artifact, or runtime setup failure.

## Artifact Locations
- Refer to [`artifact_paths.md`](./artifact_paths.md) and [`playwright_capture_contract.md`](./playwright_capture_contract.md).

## Reuse Boundaries
- Reuse for any UI/document analysis validation step.
- Excludes visual baselines unique to one feature unless explicitly added downstream.
