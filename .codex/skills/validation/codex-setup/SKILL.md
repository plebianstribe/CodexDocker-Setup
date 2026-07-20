---
name: codex-setup
description: Reusable setup skill for building reproducible Python, API, UI, and integration test workflows with shared naming rules, artifact path contracts, and pass/fail gates. Use when Codex needs to bootstrap or standardize development and integration test planning across similar coding projects.
---

# Codex Setup

Use this skill to establish reusable test instructions and contracts before feature implementation.

## Required Inputs
- Project root path.
- Planned implementation steps.
- Test scopes to support (`python`, `api`, `ui`, `integration`).

## Workflow
1. Read [`references/SKILLS_INDEX.md`](references/SKILLS_INDEX.md) to map implementation steps to reusable skills.
2. Select baseline test execution templates from:
- [`references/TESTS_PYTHON.md`](references/TESTS_PYTHON.md)
- [`references/TEST_UI.md`](references/TEST_UI.md)
- [`references/make_tests.md`](references/make_tests.md)
- [`references/make_apitests.md`](references/make_apitests.md)
- [`references/make_integrationtests.md`](references/make_integrationtests.md)
3. Apply shared contracts:
- [`references/test_naming_conventions.md`](references/test_naming_conventions.md)
- [`references/artifact_paths.md`](references/artifact_paths.md)
- [`references/mock_data_contracts.md`](references/mock_data_contracts.md)
- [`references/api_test_contract.md`](references/api_test_contract.md)
- [`references/playwright_capture_contract.md`](references/playwright_capture_contract.md)
4. Ensure every generated test plan includes purpose, required inputs, expected outputs, command patterns, pass/fail criteria, artifact locations, and reuse boundaries.

## Output Requirements
- Produce deterministic command sequences suitable for repeated use.
- Keep step-specific implementation details out of shared templates.
- Emit artifact locations using the shared contract paths.

## Validation
- Confirm all referenced files exist before use.
- Reject plans that omit pass/fail gates or artifact destinations.
- Reject test names that violate naming conventions.
