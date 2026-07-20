# Contract: Test Naming Conventions

## Purpose
Standardize test naming so suites remain discoverable and maintainable.

## Required Inputs
- Test type (`unit`, `integration`, `api`, `ui`).
- Feature/module identifier.

## Expected Outputs
- File and test IDs that match naming rules.

## Command Patterns
- Python files: `tests/<area>/test_<feature>.py`
- Python test functions: `test_<behavior>__<condition>()`
- UI specs: `<feature>.spec.ts`

## Pass/Fail Criteria
- Pass: names are deterministic, snake_case for Python and kebab/snake as framework requires.
- Fail: ambiguous, duplicate, or non-discoverable naming.

## Artifact Locations
- N/A (applies to naming only).

## Reuse Boundaries
- Global naming rules for all planned steps.
