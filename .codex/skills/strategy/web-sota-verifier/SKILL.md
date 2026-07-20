---
name: web-sota-verifier
description: Verify a refined concept with citation-backed web evidence for novelty, SOTA alignment, competitor pressure, and implementation feasibility; usually invoked after idea-domain-refiner or interactive-planner subprocess outputs.
---

# Web Sota Verifier

Audit strategic claims with current web evidence, not intuition.

## When To Use
- After `$idea-domain-refiner` or `$interactive-planner` produces a concept brief/handoff packet.
- Before major build investment or GTM commitment.
- When novelty, competitive position, or implementation realism is uncertain.
- When stakeholders require source-backed decisions.

## Required Inputs
- Refined idea summary (or full concept brief).
- Target domain, market, geography, and customer segment.
- Claimed differentiators and expected outcomes.
- Key implementation assumptions to verify.

If upstream output is missing, synthesize a minimal assumption set and label it as inferred.

## Verification Workflow
1. Build verification scope and claim set.
2. Gather evidence across four source classes:
- SOTA technical sources,
- competitive landscape,
- deployment evidence,
- business/commercial signals.
3. Run novelty and overlap analysis.
4. Build competitor SWOT + strategic pressure map.
5. Mine cross-domain transferable implementation specs.
6. Issue evidence-backed strategic recommendation.

Use `references/novelty-and-swot-framework.md` for scoring.

## Output Contract
Return sections in this order:
1. Verification Scope and Claims
2. Source Quality Summary
3. SOTA Comparison and Novelty Classification
4. Competitor Map with SWOT
5. Analogous Deployments and Transferable Specs
6. Risk and Feasibility Reality Check
7. Strategic Recommendation
8. Open Evidence Gaps and Next Research Actions

## Quality Bar
- Cite load-bearing claims.
- Date-anchor high-change evidence.
- Label inference vs sourced facts.
- Avoid false precision when evidence quality is weak.
- If evidence conflicts, present both sides and resolve with rationale.

## Coordination With Refinement Skill
If refinement is shallow or assumptions are missing, return "refine first" with the exact missing inputs to request from `$idea-domain-refiner`.
