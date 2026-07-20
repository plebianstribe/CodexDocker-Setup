# Subset Validation Contract

## Deterministic Subset Rules
- Use fixed random seed recorded in output.
- Keep subset intentionally small but representative across key classes/states.
- Include known edge and failure-prone samples for changed behavior.
- Record sample IDs so reruns are identical.

## Minimum Validation Gates
- Unit tests covering changed modules/functions.
- Integration path for data -> model -> output contract.
- End-to-end workflow check for the updated user-visible capability.
- Regression checks for previously stable critical behavior.

## Go/No-Go Rule
- `GO`: all blocking tests pass and no severe regression appears.
- `NO-GO`: any blocking test fails or output contract is violated.
