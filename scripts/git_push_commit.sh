#!/usr/bin/env bash
set -euo pipefail

# Set this before running.
COMMIT_MESSAGE="Codex commit update"

if [ -z "$COMMIT_MESSAGE" ]; then
  echo "COMMIT_MESSAGE must be set."
  exit 1
fi

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "Run this script inside a git repository."
  exit 1
}

BRANCH_NAME="$(git rev-parse --abbrev-ref HEAD)"
if [ "$BRANCH_NAME" = "HEAD" ]; then
  echo "Detached HEAD detected. Switch to a branch first."
  exit 1
fi

git add -A

if git diff --cached --quiet; then
  echo "No staged changes to commit."
  exit 0
fi

git commit -m "$COMMIT_MESSAGE"
git push origin "$BRANCH_NAME"
echo "Committed and pushed on branch: $BRANCH_NAME"

