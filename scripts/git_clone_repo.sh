#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./fork-repo.sh NEW_REPO_NAME [DEST_DIR]
#
# Example:
#   ./fork-repo.sh my-new-project
#   ./fork-repo.sh my-new-project ../my-new-project

NEW_REPO_NAME="${1:-}"
DEST_DIR="${2:-$NEW_REPO_NAME}"

if [[ -z "$NEW_REPO_NAME" ]]; then
    echo "Usage: $0 NEW_REPO_NAME [DEST_DIR]"
    exit 1
fi

# Verify we're inside a git repository.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "Current directory is not a git repository."
    exit 1
}

ORIGIN_URL="$(git remote get-url origin)"

if [[ -z "$ORIGIN_URL" ]]; then
    echo "No origin remote found."
    exit 1
fi

if [[ -e "$DEST_DIR" ]]; then
    echo "Destination already exists: $DEST_DIR"
    exit 1
fi

echo "Source origin: $ORIGIN_URL"
echo "Cloning into: $DEST_DIR"

git clone "$ORIGIN_URL" "$DEST_DIR"

cd "$DEST_DIR"

echo "Removing existing origin..."
git remote remove origin

echo "Creating GitHub repo: $NEW_REPO_NAME"

#gh repo create "$NEW_REPO_NAME" \
#    --private \
#    --source=. \
#    --remote=origin \
#    --push

echo
echo "Done."
echo "New repo: $NEW_REPO_NAME"
echo "Local copy: $(pwd)"
echo "Origin: $(git remote get-url origin)"
