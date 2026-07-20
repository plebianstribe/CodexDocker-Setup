# Skill: Create Integration Tests

## Purpose
Define repeatable integration test authoring and execution across module boundaries.

## Required Inputs
- Defined integration boundaries (service-to-service/module-to-module).
- Mock/stub data contract where external dependencies exist.
- Stable environment setup instructions.

## Expected Outputs
- Integration test suite covering cross-component flows.
- Execution report and artifacts for integration runs.

## Command Patterns
- `mkdir -p tests/integration`
- `pytest -q tests/integration`
- `pytest -q tests/integration -k <flow>`

## Pass/Fail Criteria
- Pass: cross-boundary flows complete without contract mismatches.
- Fail: interface mismatch, fixture instability, or failing flow assertions.

## Artifact Locations
- Refer to [`artifact_paths.md`](./artifact_paths.md).

## Reuse Boundaries
- Reuse for any end-to-end module interaction testing.
- Excludes production load/performance profiling unless explicitly added.
