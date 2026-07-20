#!/usr/bin/env bash
set -euo pipefail

WORKSPACE_DIR="${WORKSPACE_DIR:-$PWD}"
HOME_ENV_FILE="${HOME}/.env"

if [ -z "${CODEX_API_KEY:-}" ] && [ -f "${WORKSPACE_DIR}/.env" ]; then
    # Allow recovery when .env is mounted but variables were not exported.
    CODEX_API_KEY="$(sed -n 's/^CODEX_API_KEY=//p' "${WORKSPACE_DIR}/.env" | tail -n 1 | sed 's/^"//; s/"$//')"
    export CODEX_API_KEY
fi

if [ -z "${CODEX_API_KEY:-}" ] && [ -f "${HOME_ENV_FILE}" ]; then
    CODEX_API_KEY="$(sed -n 's/^CODEX_API_KEY=//p' "${HOME_ENV_FILE}" | tail -n 1 | sed 's/^"//; s/"$//')"
    export CODEX_API_KEY
fi

if [ -z "${CODEX_API_KEY:-}" ]; then
    echo "Warning: CODEX_API_KEY is not set. Codex API calls may fail."
fi

if [ -n "${AZURE_OPENAI_BASE_URL:-}" ] && [ -z "${CODEX_API_KEY:-}" ]; then
    echo "Warning: AZURE_OPENAI_BASE_URL is set but CODEX_API_KEY is missing."
fi

if [ ! -f "${CODEX_HOME:-${HOME}/.codex}/config.toml" ]; then
    echo "Warning: Codex config.toml is missing from ${CODEX_HOME:-${HOME}/.codex}."
fi
