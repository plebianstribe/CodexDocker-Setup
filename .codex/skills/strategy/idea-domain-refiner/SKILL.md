---
name: idea-domain-refiner
description: Refine a raw idea into a domain-ready concept brief through a specified persona lens, with explicit assumptions, architecture, risks, and validation experiments; default mode is local reasoning, with optional handoff to web-sota-verifier for external evidence checks.
---

# Idea Domain Refiner

Refine ideas into domain-ready plans by forcing explicit assumptions, constraints, and execution detail for a chosen domain or persona.

## Execution Modes
- `local` (default): persona/domain refinement using provided context and explicit assumptions.
- `verified` (optional): run local refinement first, then hand off external-evidence checks to `$web-sota-verifier`.

By default this skill is local persona reasoning and does **not** require web verification.

## When To Use
- The user asks to evaluate or improve an idea "as" a specific expert/persona.
- The user needs domain-native terminology, constraints, or regulations reflected in the concept.
- The user wants an actionable roadmap, not a high-level brainstorm.
- The user or downstream workflow requires structured inputs for `$web-sota-verifier`.

## Inputs
Collect or infer:
- Idea statement (one sentence).
- Primary domain (industry/use context).
- Persona lens (role, incentives, constraints).
- Target user/customer segment.
- Business objective (revenue, cost, quality, speed, compliance).
- Constraints (budget, timeline, team size, legal boundaries, stack preferences).

If critical inputs are missing, proceed with explicit assumptions instead of stalling.

## Workflow
1. Reframe the idea in domain language.
2. Build a constraint-aware concept model.
3. Produce implementation architecture.
4. Stress-test assumptions and risks.
5. Define measurable validation experiments.
6. Score quality with `references/refinement-rubric.md` and revise weak sections.
7. If user requests external validation/current-market proof, prepare and hand off a verification packet to `$web-sota-verifier`.

## Output Contract
Return sections in this order:
1. Idea Reframe (domain/persona lens)
2. Domain Problem and JTBD
3. Solution Blueprint
4. Operating Model and Economics
5. Architecture and Integration Notes
6. Assumptions and Risk Register
7. Validation Experiments
8. 30/60/90 Day Execution Plan
9. Open Questions for Next Iteration
10. Verification Handoff Packet (only when external validation is requested)

## Quality Bar
- Keep recommendations domain-anchored, not generic.
- Quantify KPIs/thresholds where possible.
- Distinguish assumptions from facts.
- Keep uncertainty explicit.
- Provide enough detail that another operator can execute the first pilot.

## Hand-off To Web Verification
When handing off to `$web-sota-verifier`, include:
- one paragraph problem statement,
- core mechanism of differentiation,
- target segment and geography,
- implementation stack assumptions,
- top 5 assumptions requiring external evidence.

## Subprocess Use
This skill can run as a subprocess under `$interactive-planner` when persona/expert analysis is requested during planning.
