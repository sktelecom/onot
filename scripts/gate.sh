#!/usr/bin/env bash
# onot 2.0 quality gate (L1). Cumulatively strengthened per milestone.
# Evolution: M0.5 ruff+format+pytest+cov60 -> M1 cov85 -> M2 cov90(respx) -> M3 XML security
#       -> M6 API contract -> M7 frontend build+test -> M8 frozen smoke -> M9 CI invocation.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# Coverage threshold (monotonically non-decreasing). Only raises allowed as milestones progress. Current: M2=90
COV_MIN="${ONOT_COV_MIN:-90}"

echo "==> English-only guard (no Hangul)"
python scripts/check_no_hangul.py

echo "==> ruff check"
ruff check src tests

echo "==> ruff format --check"
ruff format --check src tests

echo "==> mypy"
mypy

echo "==> pytest (cov-fail-under=${COV_MIN})"
pytest --cov --cov-report=term-missing --cov-fail-under="${COV_MIN}"

# M7+: frontend build + test
echo "==> frontend (build + test)"
if [ -d "frontend/node_modules" ]; then
  (cd frontend && pnpm build && pnpm test)
else
  echo "  (skipped: frontend/node_modules missing — run 'pnpm -C frontend install' then rerun)"
fi

# M8+: Electron sidecar lifecycle (spawn->health->stop->no orphans with the dev sidecar).
# The actual frozen build/Electron packaging/Playwright-electron E2E run in M9 CI (Win/mac).
echo "==> electron sidecar lifecycle"
node --test electron/test/*.test.mjs

echo "gate OK"
