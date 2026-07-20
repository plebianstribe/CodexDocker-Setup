# Skill: Create API Tests

## Purpose
Define standardized API test creation/execution against endpoint contracts.

## Required Inputs
- API endpoint inventory and expected request/response schemas.
- Authentication strategy for tests.
- API contract and artifact path references.

## Expected Outputs
- Endpoint tests for success/failure cases.
- API run logs and machine-readable test results.

## Command Patterns
- `mkdir -p tests/api`
- `pytest -q tests/api`
- `pytest -q tests/api -k <endpoint_name>`

## Pass/Fail Criteria
- Pass: expected status codes, schema conformance, and deterministic response checks.
- Fail: schema mismatch, status code drift, auth/setup failures.

## Artifact Locations
- Refer to [`artifact_paths.md`](./artifact_paths.md) and [`api_test_contract.md`](./api_test_contract.md).

## Reuse Boundaries
- Reuse for API-level validation across future implementation phases.
- Excludes one-off load testing scripts unless promoted into shared contract.
