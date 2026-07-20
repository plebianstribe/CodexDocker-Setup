#!/usr/bin/env bash
set -euo pipefail

md_file="${1:-}"
if [[ -z "${md_file}" ]]; then
  echo "Usage: $0 <markdown-file>" >&2
  exit 1
fi

if [[ ! -f "${md_file}" ]]; then
  echo "Markdown file not found: ${md_file}" >&2
  exit 2
fi

# Use workspace-pinned dependency from /workspace/package.json.
npx --prefix /workspace --no-install markdownlint "${md_file}"
echo "Readability/lint check passed: ${md_file}"
