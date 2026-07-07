#!/bin/bash
set -euo pipefail

PROJECT_DIR="/Users/yashabutt/love-lens-pipeline"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
LAST_RUN_FILE="$PROJECT_DIR/output/.last_run_date"
LOG_FILE="$PROJECT_DIR/cron.log"

mkdir -p "$PROJECT_DIR/output"

now=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
today=$(date -u +"%Y-%m-%d")

if [ -f "$LAST_RUN_FILE" ]; then
  last_run_date=$(cat "$LAST_RUN_FILE" | tr -d ' \t\r\n') || last_run_date=""
else
  last_run_date=""
fi

if [ "$last_run_date" = "$today" ]; then
  echo "$now skipped, already done today" >> "$LOG_FILE"
  exit 0
fi

cd "$PROJECT_DIR"

if "$VENV_PYTHON" run.py && "$VENV_PYTHON" notify.py; then
  echo "$today" > "$LAST_RUN_FILE"
  echo "$now ran" >> "$LOG_FILE"
  exit 0
else
  echo "$now failed, will retry" >> "$LOG_FILE"
  exit 1
fi
