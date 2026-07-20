# Contract: Mock Data

## Purpose
Standardize mock/stub data for reliable tests.

## Required Inputs
- Data model name.
- Required fields and types.
- Valid and invalid example cases.

## Expected Outputs
- Versioned mock fixtures with schema-aligned fields.

## Command Patterns
- Fixture location: `tests/fixtures/<domain>/`
- File formats: `.json`, `.yaml`, or `.py` factories.

## Pass/Fail Criteria
- Pass: fixtures are deterministic, minimal, and schema-conformant.
- Fail: random/non-deterministic fixtures or schema drift.

## Artifact Locations
- Fixture sources: `/app/tests/fixtures/`

## Reuse Boundaries
- Reuse across unit, API, and integration tests.
- Production datasets are out of scope for this contract.
