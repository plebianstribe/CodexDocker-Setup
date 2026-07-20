# Repository Workflow Defaults

These are the default operating instructions for work in this repository.

## Change Flow

- Prefer a new git branch for non-trivial changes.
- Use branch names in the form `codex-<short-topic>` for Codex-driven work.
- Make the requested edits directly in the workspace.
- Verify the result before reporting back.
- Summarize what changed and which files were touched.
- Do not auto-commit, auto-push, or auto-merge unless the user explicitly requests it.

## Review Flow

- Show the relevant diff or review summary to the user.
- Keep unrelated changes out of the patch.
- Ask for manual review and approval before integration into the main branch.
- If the change is small and local, a commit may be useful, but only after user confirmation.
- End the response with a concrete `git diff` command that compares the original branch to the working branch, plus a short file summary.
- If a helper script exists, use it to print the original branch name, current branch name, and review commands for the user.

## Integration Flow

- Use manual approval as the default gate for merge or push.
- Favor a feature branch over direct changes on the main branch.
- Treat `git diff` and targeted runtime checks as the standard verification tools.
- If the user wants a different workflow, follow the user’s instruction instead.
- For handoff, include explicit `git merge` and `git push` commands, but leave execution to the user unless they explicitly request the agent to run them.

## Local Skill References

- See `PORTS_SKILL.md` for the repository-standard Docker host/container port mappings and service usage notes.
