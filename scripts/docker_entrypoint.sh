#!/usr/bin/env bash
set -euo pipefail

TARGET_REPO="/workspace"

if [ -d /app ]; then
    TARGET_REPO="/app"
fi

cd /workspace

if [ -z "${CODEX_API_KEY:-}" ]; then
    echo "Warning: CODEX_API_KEY is not set. Start the container with --env-file."
fi

if [ ! -f "${CODEX_HOME:-${HOME}/.codex}/config.toml" ]; then
    echo "Warning: Codex config.toml is missing from ${CODEX_HOME:-${HOME}/.codex}."
fi

/usr/local/bin/uv_setup.sh "$TARGET_REPO"

if [ -n "${CODEX_API_KEY:-}" ]; then
    tmux set-environment -g CODEX_API_KEY "$CODEX_API_KEY" || true
fi
if [ -n "${AZURE_OPENAI_BASE_URL:-}" ]; then
    tmux set-environment -g AZURE_OPENAI_BASE_URL "$AZURE_OPENAI_BASE_URL" || true
fi

exec tmux -f /etc/tmux.conf new-session -A -s codex -c "$TARGET_REPO"
