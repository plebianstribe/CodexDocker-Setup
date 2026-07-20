#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

YOLO_MODE=0
ENV_FILE=""

while (($#)); do
    case "$1" in
        --yolo)
            YOLO_MODE=1
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--yolo] [path/to/.env]"
            exit 0
            ;;
        -*)
            echo "Error: unknown option: $1"
            echo "Usage: $0 [--yolo] [path/to/.env]"
            exit 1
            ;;
        *)
            if [ -n "${ENV_FILE}" ]; then
                echo "Error: multiple env files provided."
                echo "Usage: $0 [--yolo] [path/to/.env]"
                exit 1
            fi
            ENV_FILE="$1"
            shift
            ;;
    esac
done

ENV_FILE="${ENV_FILE:-${REPO_ROOT}/.env}"

if [ ! -f "${ENV_FILE}" ]; then
    echo "Error: env file not found: ${ENV_FILE}"
    exit 1
fi

get_env_value() {
    local key="$1"
    local file="$2"
    local line
    line="$(sed -n "s/^[[:space:]]*${key}[[:space:]]*=[[:space:]]*//p" "${file}" | tail -n 1)"
    line="${line%%#*}"
    line="$(printf "%s" "${line}" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
    line="$(printf "%s" "${line}" | sed 's/^"//; s/"$//; s/^'\''//; s/'\''$//')"
    printf "%s" "${line}"
}

REMOTE_URL=""
for key in CODEX_BASE_URL REMOTE_URL REMOTEURL AZURE_OPENAI_BASE_URL; do
    value="$(get_env_value "${key}" "${ENV_FILE}")"
    if [ -n "${value}" ]; then
        REMOTE_URL="${value}"
        break
    fi
done

if [ -z "${REMOTE_URL}" ]; then
    echo "Error: no remote URL found in ${ENV_FILE}."
    echo "Set one of: REMOTEURL, REMOTE_URL, CODEX_BASE_URL, AZURE_OPENAI_BASE_URL"
    exit 1
fi

MODEL_PROVIDER="$(get_env_value "CODEX_MODEL_PROVIDER" "${ENV_FILE}")"
MODEL_PROVIDER="${MODEL_PROVIDER:-azure}"

MODEL_NAME="$(get_env_value "CODEX_MODEL" "${ENV_FILE}")"
MODEL_NAME="${MODEL_NAME:-gpt-5.3.codex}"

REASONING_EFFORT="$(get_env_value "CODEX_MODEL_REASONING_EFFORT" "${ENV_FILE}")"
REASONING_EFFORT="${REASONING_EFFORT:-low}"

API_ENV_KEY="$(get_env_value "CODEX_API_ENV_KEY" "${ENV_FILE}")"
API_ENV_KEY="${API_ENV_KEY:-CODEX_API_KEY}"

OUTPUT_CONFIG="./.codex/config.toml"
FULL_PERMS_LINE=""
if [ "${YOLO_MODE}" -eq 1 ]; then
    FULL_PERMS_LINE='sandbox_mode = "danger-full-access"'
fi

mkdir -p "$(dirname "${OUTPUT_CONFIG}")"

cat > "${OUTPUT_CONFIG}" <<EOF
model_provider = "${MODEL_PROVIDER}"
model = "${MODEL_NAME}"
model_reasoning_effort = "${REASONING_EFFORT}"
personality = "pragmatic"
approvals_reviewer = "user"
${FULL_PERMS_LINE}

[model_providers.${MODEL_PROVIDER}]
name = "Azure OpenAI"
base_url = "${REMOTE_URL}"
env_key = "${API_ENV_KEY}"
wire_api = "responses"

[projects."/app"]
trust_level = "trusted"

[projects."/home"]
trust_level = "trusted"

[projects."/workspace"]
trust_level = "trusted"
EOF

echo "Wrote Codex config: ${OUTPUT_CONFIG}"
echo "Using base_url from env: ${REMOTE_URL}"
if [ "${YOLO_MODE}" -eq 1 ]; then
    echo "YOLO mode enabled: sandbox_mode=danger-full-access"
fi
