#!/usr/bin/env bash
# frozen FastAPI 사이드카 빌드(PyInstaller). 출력: <repo>/dist/onot-sidecar/.
# 지연 import되는 어댑터 의존성(spdx-tools/cyclonedx/openpyxl)과 번들 데이터(라이선스
# 전문/템플릿/i18n)를 --collect-all로 포함한다(에어갭 1급, frozen 검증 완료 — D-006/D-016).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

rm -rf build dist onot-sidecar.spec
pyinstaller --noconfirm --onedir --name onot-sidecar \
  --collect-all onot \
  --collect-all uvicorn \
  --collect-all spdx_tools \
  --collect-all cyclonedx \
  --collect-all license_expression \
  --collect-all openpyxl \
  --collect-all defusedxml \
  src/onot/api/serve.py

echo "built: dist/onot-sidecar"
