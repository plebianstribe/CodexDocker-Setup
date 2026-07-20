# Skill: Python Tests

## Purpose
Define a repeatable process for Python unit/module test execution and validation.

## Required Inputs
- Python environment with project dependencies.
- Target test scope (`all`, module path, or marker).
- Naming and artifact contracts.

## Expected Outputs
- Test run result (`pass`/`fail`) and summary metrics.
- Captured logs/artifacts saved under standardized locations.

## Command Patterns
- `pytest -q`
- `pytest -q tests/<module>`
- `pytest -q -k <pattern>`

## Pass/Fail Criteria
- Pass: `pytest` exits `0` and no unexpected skips/errors.
- Fail: non-zero exit, import/runtime errors, or failing assertions.

## Artifact Locations
- Refer to [`artifact_paths.md`](./artifact_paths.md).

## Reuse Boundaries
- Reuse for any Python test execution in Steps 1-5.
- Do not embed feature-specific assertions into this base skill.
