#!/usr/bin/env bash
set -euo pipefail

JUPYTER_HOME="/home/jupyter"
JUPYTER_PORT="${JUPYTER_PORT:-8888}"
JUPYTER_IP="${JUPYTER_IP:-0.0.0.0}"
JUPYTER_TOKEN="${JUPYTER_TOKEN:-}"

mkdir -p "${JUPYTER_HOME}"

if [ ! -e "${JUPYTER_HOME}/workspace" ] && [ -d /workspace ]; then
    ln -s /workspace "${JUPYTER_HOME}/workspace"
fi

if [ ! -e "${JUPYTER_HOME}/app" ] && [ -d /app ]; then
    ln -s /app "${JUPYTER_HOME}/app"
fi

echo "Starting JupyterLab on ${JUPYTER_IP}:${JUPYTER_PORT} with root ${JUPYTER_HOME}"
if [ -n "${JUPYTER_TOKEN}" ]; then
    exec jupyter lab \
        --ip="${JUPYTER_IP}" \
        --port="${JUPYTER_PORT}" \
        --no-browser \
        --ServerApp.root_dir="${JUPYTER_HOME}" \
        --ServerApp.token="${JUPYTER_TOKEN}" \
        --ServerApp.allow_remote_access=True
fi

exec jupyter lab \
    --ip="${JUPYTER_IP}" \
    --port="${JUPYTER_PORT}" \
    --no-browser \
    --ServerApp.root_dir="${JUPYTER_HOME}" \
    --ServerApp.allow_remote_access=True
