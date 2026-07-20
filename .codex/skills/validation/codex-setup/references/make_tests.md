# Skill: Create General Tests

## Purpose
Create new test files and baseline assertions for implementation changes.

## Required Inputs
- Feature/module under test.
- Expected behavior and edge cases.
- Naming and artifact contracts.

## Expected Outputs
- New/updated test files with deterministic naming.
- Minimum happy-path + edge-case coverage aligned with requirements.

## Command Patterns
- `mkdir -p tests/<area>`
- `touch tests/<area>/test_<feature>.py`
- `pytest -q tests/<area>/test_<feature>.py`

## Pass/Fail Criteria
- Pass: tests are discoverable, readable, and pass locally.
- Fail: non-discoverable names, flaky assertions, or missing critical behavior coverage.

## Artifact Locations
- Refer to [`artifact_paths.md`](./artifact_paths.md).

## Reuse Boundaries
- Reuse as base template for test authoring across steps.
- Do not include step-specific acceptance text in this shared template.
