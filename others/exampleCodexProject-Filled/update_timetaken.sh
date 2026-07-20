#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <STAGE-ID> <ONE-LINE-DESCRIPTION>"
  exit 1
fi

STAGE_ID="$1"
shift
DESCRIPTION="$*"
TIMETAKEN_FILE="TimeTaken.md"
NOW_UTC8="$(date -u -d '+8 hours' '+%Y-%m-%d %H:%M:%S')"

if [ ! -f "$TIMETAKEN_FILE" ]; then
  cat > "$TIMETAKEN_FILE" <<'HEADER'
# TimeTaken
HEADER
fi

{
  echo "- Current time (UTC+8): ${NOW_UTC8}"
  echo "- Stage completed: ${STAGE_ID}"
  echo "- Progress: ${DESCRIPTION}"
} >> "$TIMETAKEN_FILE"

echo "Updated ${TIMETAKEN_FILE} with ${STAGE_ID} at ${NOW_UTC8} (UTC+8)."
