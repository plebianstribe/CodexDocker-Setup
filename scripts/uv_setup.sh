#!/usr/bin/env bash
set -euo pipefail

WORKDIR="${1:-/workspace}"
cd "$WORKDIR"

mkdir -p "$WORKDIR/.codex-cache"
REQ_FILE=""
for CANDIDATE in pipreqs.txt requirements.txt reqs.txt; do
    if [ -f "$CANDIDATE" ]; then
        REQ_FILE="$CANDIDATE"
        break
    fi
done

if [ ! -f pyproject.toml ]; then
    uv init --no-readme --name workspace >/dev/null 2>&1 || uv init >/dev/null 2>&1
fi

if [ -n "$REQ_FILE" ]; then
    REQ_HASH_FILE="$WORKDIR/.codex-cache/_uv_requirements.sha256"
    NEW_HASH="$(sha256sum "$REQ_FILE" | awk '{print $1}')"
    OLD_HASH=""
    if [ -f "$REQ_HASH_FILE" ]; then
        OLD_HASH="$(cat "$REQ_HASH_FILE")"
    fi

    if [ "$NEW_HASH" != "$OLD_HASH" ]; then
        uv add -r "$REQ_FILE"
        echo "$NEW_HASH" > "$REQ_HASH_FILE"
    fi
fi
