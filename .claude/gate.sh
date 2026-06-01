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

echo "==> pytest (cov-fail-under=${COV_MIN})"
pytest --cov --cov-report=term-missing --cov-fail-under="${COV_MIN}"

echo "gate OK"
