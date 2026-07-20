---
name: update-dependencies
description: Update Python dependency manifests and runtime packages safely with reproducible verification. Use when a required tool/library is missing (for example `pytest`), when adding/removing dependencies in `pyproject.toml` or `requirements.txt`, or when dependency changes must be validated with install and test logs.
---

# Update Dependencies

Use this skill to apply dependency changes with traceable verification.

## Inputs
- Project root path.
- Dependency change request (package name/version and target manifests).
- Validation command(s) proving the dependency is usable.

## Workflow
1. Read current dependency manifests (`pyproject.toml`, `requirements.txt`).
2. Add or update package entries in all required manifests.
3. Install/update packages in the active virtual environment.
4. Verify installation (`python -m pip show <pkg>` or `python -m <tool> --version`).
5. Run target validation tests and store logs in artifact paths.
6. Record blockers and exact remediation if validation fails.

## Validation Requirements
- Manifest entries are present and consistent.
- Install command exits successfully.
- Verification command confirms package availability.
- At least one target workflow/test command runs successfully.

## References
- [`references/dependency_update_checklist.md`](references/dependency_update_checklist.md)
