#!/usr/bin/env bash
set -euo pipefail

# Set these before running.
BRANCH_NAME="codex/update-branch-name"
COMMIT_MESSAGE="Codex changes"

if [ -z "$BRANCH_NAME" ] || [ -z "$COMMIT_MESSAGE" ]; then
  echo "BRANCH_NAME and COMMIT_MESSAGE must be set."
  exit 1
fi

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "Run this script inside a git repository."
  exit 1
}

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]; then
  git checkout -B "$BRANCH_NAME"
fi

git add -A

if git diff --cached --quiet; then
  echo "No staged changes to commit."
  exit 0
fi

git commit -m "$COMMIT_MESSAGE"
git push -u origin "$BRANCH_NAME"
echo "Pushed branch: $BRANCH_NAME"

