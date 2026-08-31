#!/bin/bash
# Optional hourly-cron fallback for the launchd slot agents. Runs the correct
# slot when the current local hour is inside its window. Delegates to
# run_slot.sh, which holds the once-per-day marker and the atomic lock, so this
# is safe to run alongside the launchd agents (nothing double-posts).
set -euo pipefail

PROJECT_DIR="/Users/yashabutt/love-lens-pipeline"
hour=$((10#$(date +%H)))   # local hour, 0-23

# Morning slot window: 07:00-11:59 local.
if [ "$hour" -ge 7 ] && [ "$hour" -lt 12 ]; then
  "$PROJECT_DIR/run_slot.sh" morning
fi

# Evening slot window: 18:00-22:59 local.
if [ "$hour" -ge 18 ] && [ "$hour" -lt 23 ]; then
  "$PROJECT_DIR/run_slot.sh" evening
fi
