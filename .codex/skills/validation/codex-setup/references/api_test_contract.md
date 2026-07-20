# Contract: API Test

## Purpose
Define minimum API validation requirements for request/response testing.

## Required Inputs
- Endpoint method/path.
- Request payload schema.
- Expected response schema/status.

## Expected Outputs
- API tests covering success, validation failure, and auth/permission behavior.

## Command Patterns
- Positive case: `test_<endpoint>__returns_<status>()`
- Negative case: `test_<endpoint>__rejects_<invalid_case>()`

## Pass/Fail Criteria
- Pass: status code, key response fields, and schema validation all succeed.
- Fail: mismatch in any contract component or undocumented behavior changes.

## Artifact Locations
- API artifacts: `/app/artifacts/api/<run_id>/`

## Reuse Boundaries
- Reuse for all endpoint-level checks.
- Business-specific scenario matrices belong to downstream feature tests.
