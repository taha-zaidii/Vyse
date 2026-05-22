#!/usr/bin/env bash
# scripts/run_local.sh — boot Vyse end-to-end locally (no Docker).
# Requires Python 3.11+ and Node 20+.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Backend
if [ ! -d "backend/.venv" ]; then
  echo "[setup] creating Python venv…"
  python3 -m venv backend/.venv
  source backend/.venv/bin/activate
  pip install -r backend/requirements.txt
else
  source backend/.venv/bin/activate
fi

# Run backend in background
echo "[run] starting backend on :8000…"
( cd backend && python -m vyse ) &
BACK_PID=$!

# Dashboard
echo "[run] installing dashboard deps if needed…"
( cd dashboard && [ -d node_modules ] || npm install )

echo "[run] starting dashboard on :3000…"
( cd dashboard && npm run dev ) &
DASH_PID=$!

trap "kill $BACK_PID $DASH_PID 2>/dev/null || true" EXIT INT TERM

wait
