#!/usr/bin/env bash
set -euo pipefail

root="${1:-}"
if [[ -z "${root}" ]]; then
  echo "Usage: $0 <skills-root>" >&2
  exit 1
fi

mapfile -t skill_files < <(find "${root}" -type f -name 'SKILL.md' | sort)
if [[ ${#skill_files[@]} -eq 0 ]]; then
  echo "No SKILL.md files found under ${root}" >&2
  exit 2
fi

declare -a names=()
for f in "${skill_files[@]}"; do
  name="$(awk 'BEGIN{s=0} /^---$/{if(s==0){s=1;next}else{exit}} s==1 && /^name:/{sub(/^name:[[:space:]]*/, "", $0); gsub(/"/, "", $0); print; exit}' "$f")"
  if [[ -n "${name}" ]]; then
    names+=("${name}")
  fi
done

for f in "${skill_files[@]}"; do
  src="$(awk 'BEGIN{s=0} /^---$/{if(s==0){s=1;next}else{exit}} s==1 && /^name:/{sub(/^name:[[:space:]]*/, "", $0); gsub(/"/, "", $0); print; exit}' "$f")"
  [[ -z "${src}" ]] && continue
  for n in "${names[@]}"; do
    [[ "${n}" == "${src}" ]] && continue
    if rg -q "\\b${n}\\b" "$f"; then
      echo "${src} -> ${n}"
    fi
  done
done | sort -u
