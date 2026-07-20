#!/usr/bin/env bash
set -euo pipefail

repo_root="${1:-/app}"
cd "$repo_root"

current_branch="$(git branch --show-current)"
original_branch="${ORIGINAL_BRANCH:-main}"

if git show-ref --verify --quiet "refs/remotes/origin/${original_branch}"; then
    origin_ref="origin/${original_branch}"
else
    origin_ref="${original_branch}"
fi

printf 'Original branch: %s\n' "$original_branch"
printf 'Current branch: %s\n' "$current_branch"
printf '\n'
printf 'Review diff command:\n'
printf '  git diff %s...%s -- .\n' "$origin_ref" "$current_branch"
printf '\n'
printf 'Edited files:\n'
git diff --name-only "$origin_ref"...HEAD -- .
printf '\n'
printf 'Manual integration commands:\n'
printf '  git checkout %s\n' "$original_branch"
printf '  git merge %s\n' "$current_branch"
printf '  git push origin %s\n' "$current_branch"

