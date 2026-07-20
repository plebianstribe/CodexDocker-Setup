# Report Structure Reference

Use this structure for deterministic architecture reports:

1. `# Skills Architecture and Functional Flow`
2. `## Scope`
3. `## Skills Overview` table:
   - `Skill`
   - `Utility Group`
   - `One-line Functionality`
   - `Passes Into`
4. `## High-Level Hierarchy` (Mermaid flowchart)
5. `## Dependency and Loop Diagram` (Mermaid flowchart)
6. `## Utility Groups and Explicit Pass-Through`
   - Goals/Planning
   - Local testing and validation
   - Online verification and strategy
   - System/tooling
7. `## Shared Contracts`
8. `## Main Closed Loops`
9. `## Reliability Notes`

Conventions:
- Mark inferred edges with `(inferred)`; keep explicit edges untagged.
- Keep one-line functionality under 24 words.
- Prefer short bullets over long prose.
