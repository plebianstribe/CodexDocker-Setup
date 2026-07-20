# Contract: Artifact Paths

## Purpose
Define stable output paths for all test artifacts.

## Required Inputs
- Test type and run identifier (timestamp or CI build ID).

## Expected Outputs
- Artifacts written to deterministic directories.

## Command Patterns
- Root: `artifacts/`
- Python logs/results: `artifacts/python/<run_id>/`
- API logs/results: `artifacts/api/<run_id>/`
- Integration logs/results: `artifacts/integration/<run_id>/`
- UI captures/reports: `artifacts/ui/<run_id>/`

## Pass/Fail Criteria
- Pass: every run emits artifacts under the correct typed directory.
- Fail: artifacts written outside the structure or missing required run folder.

## Artifact Locations
- Canonical location root: `/app/artifacts/`

## Reuse Boundaries
- Shared by all test-related skills; do not redefine per step unless versioned.
