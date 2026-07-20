---
name: interactive-planner
description: Run an interactive planning workflow that boots from an existing folder or referenced script, resolves scope with the user, and escalates persona-specific subproblems through idea-domain-refiner for structured recommendations.
---

# Interactive Planner

Execute a concise discovery workflow that improves planning quality while minimizing unnecessary back-and-forth.

## Scope Boundary
- Use this skill for interactive pre-implementation planning.
- If the user requests domain/persona specialization at any point, invoke `$idea-domain-refiner` as a subprocess and fold its outputs into planning artifacts.

## Required Inputs
- User request and success criteria.
- Working repository path.
- Optional bootstrap artifact from user:
  - existing folder to analyze, or
  - referenced script/file to use as starting point.

## Workflow
1. Restate scope in 2-4 lines.
2. Inspect repository context for instructions (`AGENTS.md`, local policy files, goal templates, relevant docs).
3. If a bootstrap folder/script is provided, inspect it first and extract:
- current behavior,
- constraints and assumptions,
- reusable components,
- obvious gaps vs requested outcome.
4. Extract constraints, non-goals, dependencies, governance artifacts, and missing inputs.
5. Ask only high-impact clarifying questions for material unknowns.
6. Persona/expertise subprocess rule:
- If initial prompt or follow-up asks for analysis "as" a specific persona/expert lens, run `$idea-domain-refiner` as a subprocess.
- Pass the latest scoped problem statement, persona lens, constraints, and requested outcomes.
- Capture subprocess outputs as structured recommendations and assumptions.
7. Produce an integrated functional planning view that combines repository analysis + user clarifications + subprocess recommendations.
8. Request user review/approval, then proceed to deeper planning only after alignment.

## Clarification Rules
- Prefer brief, high-signal summaries and focused questions.
- Ask questions only when ambiguity is material; infer from repository context where safe.
- Prioritize questions in this order:
  1. domain and success criteria
  2. target users and operating context
  3. required functional scope and explicit exclusions
  4. technical constraints (stack, infra, compliance, budget, timeline)
  5. acceptance checks and rollout expectations
- Group questions into a compact batch.
- If user does not answer non-critical unknowns, continue with explicit assumptions.

## Functional Setup Pass
Before full planning, convert user intent into a functional model:
1. Goal statement: one sentence.
2. Functional pillars: 3-7 core capability areas.
3. For each pillar capture: problem, inputs/outputs, dependencies/constraints, measurable done criteria.
4. Risk scan: unknowns, assumptions, likely blockers, mitigation path.
5. Planning readiness decision: ready for full planning or blocked pending specific user input.

## Output Format
Use this structure for the planning review artifact:

```md
# Interactive Planning View

## Scope Summary
- ...

## Bootstrap Analysis (Folder/Script)
- Source:
- Current State:
- Reusable Assets:
- Gaps:

## Constraints and Repository Policies
- ...

## Clarifications Asked
- Question -> Answer / Assumption

## Persona Subprocess Findings (if any)
- Persona:
- Key Recommendations:
- Assumptions:
- Risks:

## Functional Goal View
### 1) <Pillar>
- Problem:
- Inputs:
- Outputs:
- Dependencies/Constraints:
- Done Criteria:

## Open Risks and Assumptions
- ...

## Initial Plan of Action
1. ...
2. ...
3. ...

## Review Gate
- Items requiring user confirmation before full planning:
  - ...
```

If a repository already has a goals template (for example `GOALS.md`), mirror its structure while preserving the sections above.

## Completion Criteria
This skill run is complete when:
1. The user has a concise, reviewable planning view.
2. Major ambiguities are answered or explicitly assumed.
3. Bootstrap folder/script context is integrated into the plan.
4. Persona/expert requests are handled via `$idea-domain-refiner` and integrated.
5. The user can approve or revise before implementation planning starts.
