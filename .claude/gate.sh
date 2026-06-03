#!/usr/bin/env bash
# onot 2.0 quality gate (L1). 마일스톤별 누적 강화.
# 진화: M0.5 ruff+format+pytest+cov60 → M1 cov85 → M2 cov90(respx) → M3 XML보안
#       → M6 API계약 → M7 frontend build+test → M8 frozen smoke → M9 CI 호출.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

# 커버리지 임계(단조 비감소). 마일스톤 진행에 따라 상향만 허용. 현재: M2=90
COV_MIN="${ONOT_COV_MIN:-90}"

echo "==> ruff check"
ruff check src tests

echo "==> ruff format --check"
ruff format --check src tests

echo "==> mypy"
mypy

echo "==> pytest (cov-fail-under=${COV_MIN})"
pytest --cov --cov-report=term-missing --cov-fail-under="${COV_MIN}"

# M7+: 프론트엔드 빌드 + 테스트
echo "==> frontend (build + test)"
if [ -d "frontend/node_modules" ]; then
  (cd frontend && pnpm build && pnpm test)
else
  echo "  (skipped: frontend/node_modules 없음 — 'pnpm -C frontend install' 후 재실행)"
fi

# M8+: Electron 사이드카 수명주기(dev 사이드카로 spawn→health→stop→고아 없음).
# 실제 frozen 빌드/Electron 패키징/Playwright-electron E2E는 M9 CI(Win/mac)에서.
echo "==> electron sidecar lifecycle"
node --test electron/test/*.test.mjs

echo "gate OK"
