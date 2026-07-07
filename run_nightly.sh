#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
# cron example: 0 9 * * * /Users/yashabutt/love-lens-pipeline/run_nightly.sh
# The Mac must be awake and plugged in for cron to fire reliably.
source .venv/bin/activate
python run.py
python notify.py
