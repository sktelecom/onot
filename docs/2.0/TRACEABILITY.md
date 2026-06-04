# onot 2.0 Traceability Matrix

Plan requirements ↔ milestones ↔ verification tests ↔ verifier verdict. Status: todo /
doing / done / deferred. A deferred item must have a DECISIONS rationale. If any
requirement is unmapped, that milestone does not pass.

| ID | Plan requirement | Milestone | Status | Evidence commit | Verification test | verifier |
|----|------------------|-----------|--------|-----------------|-------------------|----------|
| R-INF-1 | src-layout package skeleton + pyproject (3.11+) | scaffold | done | (scaffold) | pytest collection | - |
| R-INF-2 | gate.sh L1 (ruff/format/pytest/cov + frontend + electron) | scaffold~M8 | done | (cumulative) | gate.sh run | monotonic hardening |
| R-INF-3 | TRACEABILITY/DECISIONS upkeep | scaffold | done | (all milestones) | file updates | D-001~017 |
| R-S1 | license-expression/spdx-tools API verification | M0 | done | (M0 spike) | spikes/s1_license_spdx | PASS (D-004) |
| R-S2 | SPDX 3.0 support maturity | M0 | deferred | (M0 spike) | spikes/s2 probe | 3.0 input split off as follow-up (D-005) |
| R-S3 | frozen importlib.resources access | M0 | done | (M0 spike) | spikes/s3_frozen | PASS, '/' chaining (D-006) |
| R-S4 | Electron+PyInstaller sidecar lifecycle | M8 | done | (M8) | electron/test/sidecar.test, frozen startup | PASS (D-016) |
| R-S5 | PDF path confirmed | M8 | done | (M8) | main.mjs export-pdf, App pdf path | printToPDF decision (D-016) |
| R-VS | vertical slice Excel→domain→HTML→CLI | M0.5 | done | (M0.5) | tests/e2e/test_slice, tests/ingest/test_excel_robust | L1 green 96% + L3 review applied (D-009) |
| R-DOM-1 | 8 domain models + validation rules | M1 | done | (M1) | tests/unit/test_models, test_errors | L1/L2 PASS, L3 LGTM |
| R-DOM-2 | deterministic serialization/sort stability | M1 | done | (M1) | test_models, tests/license/test_resolve | L2 PASS |
| R-LIC-1 | expression resolution matrix (OR/AND/WITH/+) | M2 | done | (M2) | tests/license/test_expression, test_resolver | L1/L2 PASS, L3 blocking resolved |
| R-LIC-2 | air-gap 100% local (full texts bundled) | M2 | done | (M2) | test_resolver, test_catalog | L2 demonstrated (NETWORK=0) |
| R-LIC-3 | cache determinism/invalidation | M2 | done | (M2) | tests/license/test_cache | L2 PASS |
| R-ING-1 | 4 adapters (spdx/cdx/excel) + auto-detection | M3 | done | (M3) | tests/ingest/test_{spdx,cyclonedx,detect,registry} | L1/L2 PASS, L3 blocking resolved |
| R-ING-2 | XXE/XML-bomb defense | M3 | done | (M3) | tests/ingest/test_xml_security | L2 demonstrated, UTF-16 bypass·SPDX RDF supplemented |
| R-ING-3 | cross-format equivalence | M3 | done | (M3) | tests/ingest/test_equivalence | L2 PASS |
| R-REN-1 | 4 renderers (html/text/md/pdf) | M4 | done | (M4) | tests/rendering/test_renderers, test_golden | L1/L2 PASS, L3 blocking 0 |
| R-REN-2 | HTML autoescape (escape regression) | M4 | done | (M4) | tests/rendering/test_escape | L2 demonstrated |
| R-REN-3 | i18n catalog ko/en consistency | M4 | done | (M4) | tests/rendering/test_i18n | L2 PASS |
| R-CLI-1 | Typer CLI + exit code contract | M5 | done | (M5) | tests/cli/test_cli | L1/L2 PASS, L3 2 blocking resolved |
| R-API-1 | FastAPI parse/render/formats/healthz | M6 | done | (M6) | tests/api/test_api | L1/L2 PASS, L3 blocking 0 |
| R-API-2 | upload/path traversal validation | M6 | done | (M6) | tests/api/test_security | L2 demonstrated (traversal·XXE·413) |
| R-FE-1 | React upload→preview→download | M7 | done | (M7) | frontend vitest | L1/L2 PASS, L3 2 blocking resolved |
| R-FE-2 | a11y + i18n missing keys 0 | M7 | done | (M7) | App.test (axe), i18n.test | L2 demonstrated (axe 0, parity) |
| R-EL-1 | Electron sidecar lifecycle | M8 | done | (M8) | electron/test/sidecar.test | L1/L2 PASS, L3 3 blocking resolved |
| R-EL-2 | printToPDF | M8 | done | (M8) | App.test (pdf path), main.mjs | unit verified, real-startup E2E in M9 |
| R-CI-1 | GH Actions Win+macOS matrix | M9 | done | (M9) | .github/workflows/ci.yml | YAML verified, runs on push |
| R-CI-2 | Playwright-electron E2E | M9 | done | (M9) | electron/e2e/app.e2e.mjs | spec written, runs in CI |
