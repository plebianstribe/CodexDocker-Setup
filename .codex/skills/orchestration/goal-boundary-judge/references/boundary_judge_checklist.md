# Boundary Judge Checklist

## Sprint-Fit Heuristic
A well-scoped goal should fit one window:
- 2-day sprint (tight, implementation-focused)
- 5-day sprint (moderate feature slice)
- 10-day sprint (complex but bounded capability)

If no realistic mapping exists:
- too narrow/fragmented -> candidate `mergeup`
- too broad/ambiguous -> candidate `breakdown`

## Quality Gates
- Every step has testable acceptance criteria.
- Every step has required tests/evidence.
- Stage map exists and references only valid step IDs.
- Unlock conditions are concrete and deterministic.
- Risks/blockers are explicit.
- New live blockers are reflected in step status and blocker lists.
- User-verified live PASS claims are tracked as explicit evidence source tags.

## Complexity Delta Rules
- `minimal`: requirements fit by tightening existing acceptance/evidence, without new step proliferation.
- `acceptable`: limited additions are justified by concrete user capability deltas.
- `overgrown`: change introduces broad step explosion, mixed ownership, or unstable dependencies.

## Action Decision Rules
- `overgrown` strongly biases `breakdown` unless strong coupling requires `update` first.
- `minimal` with duplication/fragmentation strongly biases `mergeup`.
- `acceptable` generally stays in `update|create` depending on overlap and ownership.

## Ambiguity Rule
If the action cannot be chosen confidently from objective/scope/evidence, require user confirmation before edits.
