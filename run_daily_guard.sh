#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/yashabutt/love-lens-pipeline"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
LOG_FILE="$PROJECT_DIR/cron.log"

mkdir -p "$PROJECT_DIR/output"

# Local time (not UTC) so slots line up with the audience's day.
today=$(date +%F)
hour=$((10#$(date +%H)))          # 0-23, leading zero stripped
now=$(date +"%Y-%m-%d %H:%M:%S %Z")

# Run one slot (morning/evening) at most once per local day. Each slot generates
# into its own output/<date>-<slot> folder (LOVELENS_SLOT) so the evening batch
# never overwrites the morning batch that's still awaiting approval.
run_slot() {
  slot="$1"
  marker="$PROJECT_DIR/output/.last_run_$slot"
  last=""
  [ -f "$marker" ] && last=$(tr -d ' \t\r\n' < "$marker")
  if [ "$last" = "$today" ]; then
    return 0
  fi
  cd "$PROJECT_DIR"
  if LOVELENS_SLOT="$slot" "$VENV_PYTHON" run.py \
     && LOVELENS_SLOT="$slot" "$VENV_PYTHON" notify.py; then
    echo "$today" > "$marker"
    echo "$now ran $slot" >> "$LOG_FILE"
  else
    echo "$now failed $slot, will retry" >> "$LOG_FILE"
  fi
}

# Morning slot: first cron tick in the 07:00-11:59 local window.
if [ "$hour" -ge 7 ] && [ "$hour" -lt 12 ]; then
  run_slot morning
fi

# Evening slot: first cron tick in the 18:00-22:59 local window.
if [ "$hour" -ge 18 ] && [ "$hour" -lt 23 ]; then
  run_slot evening
fi
