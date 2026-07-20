---
name: foldersummary-report
description: Generate structured markdown architecture reports for a folder of skills or modules, including grouped capability summaries, dependency/hand-off mapping, and closed-loop detection. Use when a user asks for skill architecture documentation, dependency diagrams, or a reusable folder-summary report workflow.
---

# Folder Summary Report

## Inputs
1. Target root folder (for example `.../skills`).
2. Output markdown file path.
3. Optional grouping rules (for example by parent directory or by utility labels).

## Required Resources
- Read `references/report_structure.md` before writing the report.
- Use `scripts/skill_dep_map.sh` to extract dependency edges and loop candidates.
- Use `scripts/markdown_readability_check.sh` to run the mandatory readability/lint check.
- Require workspace dependency: `/workspace/package.json` must include pinned `markdownlint-cli`.

## Workflow
1. Enumerate all `SKILL.md` files under the target root.
2. Extract each skill `name` and `description` from frontmatter.
3. Detect explicit cross-skill references by scanning skill names in each SKILL body.
4. Build:
   - overview table (`Skill`, `Group`, `One-line Functionality`, `Passes Into`),
   - grouped sections by utility (goals, testing, verification, system/tooling),
   - architecture diagrams (hierarchy and dependency/loop view).
5. Cross-check links and loops with `scripts/skill_dep_map.sh`.
6. Write the final report to the requested markdown path.
7. Always run markdown readability/lint checks with:
   - `scripts/markdown_readability_check.sh <output-markdown-path>`
8. Treat the report as incomplete if the readability check fails.

## Output Contract
1. File `skills-architecture.md` (or requested target path) containing:
   - concise scope statement,
   - short overview table for all discovered skills,
   - hierarchy diagram,
   - dependency/loop diagram,
   - utility-group sections with explicit pass-through links,
   - closed-loop summary.
2. Deterministic wording for edge statements when possible.
3. No fabricated dependencies; only explicit or clearly labeled inferred links.
4. Mandatory readability check executed and passed for the output markdown file.

## Quality Bar
- Keep one-line descriptions short and specific.
- Distinguish hard links (explicit in files) vs inferred links.
- Prefer portable markdown with Mermaid diagrams for visualization.
- Never skip readability checks; run `scripts/markdown_readability_check.sh` on every report.
