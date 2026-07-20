# Skills Index (Validation Lane)

## Purpose
Map implementation and QA activities to reusable validation skills and shared contracts.

## Core Validation Skills
- `../model-validation-qa/SKILL.md`: deterministic subset gating for model-impacting updates.
- `../playwright-testing-qa/SKILL.md`: deterministic browser QA capture with trace/log artifacts.
- `../update-dependencies/SKILL.md`: safe dependency manifest + install + verification workflow.

## Orchestration Interfaces
- `../../orchestration/parallel-goal-run/SKILL.md`: staged execution runner.
- `../../orchestration/goal-harsh-judge/SKILL.md`: completion gate verdicts.
- `../../orchestration/contracts/evidence.md`: objective evidence requirements.

## Template/Contract References
- `TESTS_PYTHON.md`
- `TEST_UI.md`
- `make_tests.md`
- `make_apitests.md`
- `make_integrationtests.md`
- `test_naming_conventions.md`
- `artifact_paths.md`
- `mock_data_contracts.md`
- `api_test_contract.md`
- `playwright_capture_contract.md`

## Use Mapping
1. General Python/unit/integration test standardization -> `make_tests.md` + `TESTS_PYTHON.md`.
2. API test scaffolding/contracts -> `make_apitests.md` + `api_test_contract.md`.
3. UI/browser deterministic QA -> `TEST_UI.md` + `playwright_capture_contract.md` (+ `playwright-testing-qa`).
4. Model-impacting validation gate -> `model-validation-qa` + `subset_validation_contract.md`.
5. Dependency/tooling blockers -> `update-dependencies` + `dependency_update_checklist.md`.

## Pass/Fail Rule
- Pass: selected workflow includes purpose, inputs, commands, pass/fail criteria, and artifact destinations.
- Fail: any required contract or artifact destination is missing.
