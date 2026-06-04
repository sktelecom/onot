#!/usr/bin/env bash
# Build the frozen FastAPI sidecar (PyInstaller). Output: <repo>/dist/onot-sidecar/.
# Include the lazily-imported adapter dependencies (spdx-tools/cyclonedx/openpyxl) and bundled
# data (license full texts/templates/i18n) via --collect-all (first-class air-gap, frozen-verified — D-006/D-016).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
  # Windows venv
  # shellcheck disable=SC1091
  source .venv/Scripts/activate
fi
# If there is no venv (e.g. installed directly into the system python in CI), use python/pyinstaller from the current PATH

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
