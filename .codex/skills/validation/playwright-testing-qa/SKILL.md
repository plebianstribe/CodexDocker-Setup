---
name: playwright-testing-qa
description: Run deterministic Playwright-based UI testing and capture QA for feature workflows. Use when requests mention Playwright testing, click-marker overlays, screenshot/trace/video capture, click-spacing policy enforcement, or action-log artifacts with selector, coordinates, and timestamps.
---

# Playwright Testing QA

Use this skill for Playwright-driven UI validation flows.

## Routing Rule
- Use this skill for browser UI validation.
- If the request is model-training or architecture-update validation with dataset subset gating, route to `-validation-qa`.

## Required References
Read these files before writing or running capture scripts:
- `references/selector_contracts.md`
- `references/red_dot_overlay_rules.md`
- `references/artifact_naming.md`
- `references/wait_timing_policy.md`

## Runner Contract
1. Use `scripts/wait_enforced_capture_runner.js` for paced click actions.
2. Use `scripts/click_marker_helper.js` to place persistent red markers at click coordinates.
3. Enforce `minDelayMs >= 500` and default to `700` unless the test contract states otherwise.
4. Produce required outputs:
- marked screenshots,
- trace zip,
- video,
- action log including selector, coordinates, timestamp, delta, and optional scenario metadata.

## Standard Usage Pattern
1. Define selectors for the scenario under test.
2. Run a Playwright script that uses the wait-enforced runner.
3. Save artifacts using deterministic names under `artifacts/ui/<run_id>/`.
4. Assert completion statuses and action-log policy compliance.

## Validation Checks
- Ensure expected status text for the target scenario appears.
- Ensure action log includes click entries for required actions.
- Ensure click deltas for entries after the first are `>= minDelayMs`.
