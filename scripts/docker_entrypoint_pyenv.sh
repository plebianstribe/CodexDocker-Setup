#!/usr/bin/env bash
set -euo pipefail

PYENV_ROOT="${PYENV_ROOT:-/root/.pyenv}"
PY_VER="${PYTHON_VERSION:-3.12.12}"
ENV_NAME="${PYENV_ENV_NAME:-mainEnv}"
SEED_ROOT="/opt/pyenv_seed"
TARGET_REPO="/workspace"

if [ -d /app ]; then
    TARGET_REPO="/app"
fi

export PYENV_ROOT
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"

cd /workspace

if [ -n "${CODEX_API_KEY:-}" ]; then
    export CODEX_API_KEY
fi

if [ ! -x "$PYENV_ROOT/bin/pyenv" ]; then
    if [ -x "$SEED_ROOT/bin/pyenv" ]; then
        mkdir -p "$PYENV_ROOT"
        cp -a "$SEED_ROOT"/. "$PYENV_ROOT"/
    else
        echo "pyenv seed is missing in image. Rebuild image."
        exit 1
    fi
fi

if ! command -v pyenv >/dev/null 2>&1; then
    echo "pyenv is not installed. Rebuild image."
    exit 1
fi

eval "$(pyenv init -)"
if command -v pyenv-virtualenv-init >/dev/null 2>&1; then
    eval "$(pyenv virtualenv-init -)"
fi

if ! pyenv versions --bare | grep -x "$PY_VER" >/dev/null 2>&1; then
    echo "Python $PY_VER missing in mounted pyenv root."
    exit 1
fi

if ! pyenv virtualenvs --bare | grep -x "$ENV_NAME" >/dev/null 2>&1; then
    echo "Virtualenv $ENV_NAME missing in mounted pyenv root."
    exit 1
fi

pyenv global "$ENV_NAME"
/usr/local/bin/envvar_checker.sh

cd "$TARGET_REPO"

REQ_FILE=""
for CANDIDATE in pipreqs.txt requirements.txt reqs.txt; do
    if [ -f "$CANDIDATE" ]; then
        REQ_FILE="$CANDIDATE"
        break
    fi
done

if [ -n "$REQ_FILE" ]; then
    mkdir -p "$TARGET_REPO/.codex-cache"
    REQ_HASH_FILE="$TARGET_REPO/.codex-cache/_requirements.sha256"
    NEW_HASH="$(sha256sum "$REQ_FILE" | awk '{print $1}')"
    OLD_HASH=""
    if [ -f "$REQ_HASH_FILE" ]; then
        OLD_HASH="$(cat "$REQ_HASH_FILE")"
    fi
    if [ "$NEW_HASH" != "$OLD_HASH" ]; then
        python -m pip install --upgrade pip
        pip install -r "$REQ_FILE"
        echo "$NEW_HASH" > "$REQ_HASH_FILE"
    fi
fi

if [ -n "${CODEX_API_KEY:-}" ]; then
    tmux set-environment -g CODEX_API_KEY "$CODEX_API_KEY" || true
fi
if [ -n "${AZURE_OPENAI_BASE_URL:-}" ]; then
    tmux set-environment -g AZURE_OPENAI_BASE_URL "$AZURE_OPENAI_BASE_URL" || true
fi

exec tmux -f /etc/tmux.conf new-session -A -s codex -c "$TARGET_REPO"
