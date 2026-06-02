# onot 2.0 추적성 매트릭스

플랜 요구항목 ↔ 마일스톤 ↔ 검증 테스트 ↔ verifier 판정. 상태: todo / doing / done / deferred.
deferred는 반드시 DECISIONS 근거를 가진다. 미매핑 요구항목이 있으면 해당 마일스톤은 미통과.

| ID | 플랜 요구항목 | 마일스톤 | 상태 | 근거 커밋 | 검증 테스트 | verifier |
|----|--------------|----------|------|-----------|-------------|----------|
| R-INF-1 | src-layout 패키지 골격 + pyproject(3.11+) | 스캐폴드 | doing | - | `pytest` 수집 | - |
| R-INF-2 | gate.sh L1(ruff/format/pytest/cov) | 스캐폴드 | doing | - | gate.sh 실행 | - |
| R-INF-3 | TRACEABILITY/DECISIONS 운영 | 스캐폴드 | doing | - | 파일 존재 | - |
| R-S1 | license-expression/spdx-tools API 검증 | M0 | done | (M0 스파이크) | spikes/s1_license_spdx | PASS (D-004) |
| R-S2 | SPDX 3.0 지원 성숙도 | M0 | deferred | (M0 스파이크) | spikes/s2 probe | 3.0 입력 후속 분리 (D-005) |
| R-S3 | frozen importlib.resources 접근 | M0 | done | (M0 스파이크) | spikes/s3_frozen | PASS, '/' 체이닝 (D-006) |
| R-S4 | Electron+PyInstaller 사이드카 수명주기 | M8 | sequenced | - | spikes/s4 (M8 직전) | D-008 |
| R-S5 | PDF 경로 확정 | M8 | sequenced | - | spikes/s5 (M8 직전) | D-008 |
| R-VS | 수직 슬라이스 Excel→domain→HTML→CLI | M0.5 | done | (M0.5) | tests/e2e/test_slice, tests/ingest/test_excel_robust | L1 green 96% + L3 리뷰 반영(D-009) |
| R-DOM-1 | 도메인 모델 8종 + 검증규칙 | M1 | done | (M1) | tests/unit/test_models, test_errors | L1/L2 PASS, L3 LGTM |
| R-DOM-2 | 결정적 직렬화/정렬 안정성 | M1 | done | (M1) | test_models, tests/license/test_resolve | L2 PASS |
| R-LIC-1 | 표현식 해석 매트릭스(OR/AND/WITH/+) | M2 | done | (M2) | tests/license/test_expression, test_resolver | L1/L2 PASS, L3 blocking 해소 |
| R-LIC-2 | 에어갭 100% 로컬(전문 번들) | M2 | done | (M2) | test_resolver, test_catalog | L2 실증(NETWORK=0) |
| R-LIC-3 | 캐시 결정성/무효화 | M2 | done | (M2) | tests/license/test_cache | L2 PASS |
| R-ING-1 | 4개 어댑터(spdx/cdx/excel) + 자동감지 | M3 | done | (M3) | tests/ingest/test_{spdx,cyclonedx,detect,registry} | L1/L2 PASS, L3 blocking 해소 |
| R-ING-2 | XXE/XML폭탄 방어 | M3 | done | (M3) | tests/ingest/test_xml_security | L2 실증, UTF-16 우회·SPDX RDF 보완 |
| R-ING-3 | 크로스포맷 등가성 | M3 | done | (M3) | tests/ingest/test_equivalence | L2 PASS |
| R-REN-1 | 4개 렌더러(html/text/md/pdf) | M4 | done | (M4) | tests/rendering/test_renderers, test_golden | L1/L2 PASS, L3 blocking 0 |
| R-REN-2 | HTML autoescape(이스케이프 회귀) | M4 | done | (M4) | tests/rendering/test_escape | L2 실증 |
| R-REN-3 | i18n 카탈로그 ko/en 정합성 | M4 | done | (M4) | tests/rendering/test_i18n | L2 PASS |
| R-CLI-1 | Typer CLI + exit code 계약 | M5 | done | (M5) | tests/cli/test_cli | L1/L2 PASS, L3 blocking 2건 해소 |
| R-API-1 | FastAPI parse/render/formats/healthz | M6 | done | (M6) | tests/api/test_api | L1/L2 PASS, L3 blocking 0 |
| R-API-2 | 업로드/경로 traversal 검증 | M6 | done | (M6) | tests/api/test_security | L2 실증(traversal·XXE·413) |
| R-FE-1 | React 업로드→미리보기→다운로드 | M7 | todo | - | frontend vitest/e2e | - |
| R-FE-2 | a11y + i18n 키 누락 0 | M7 | todo | - | axe/i18n 검사 | - |
| R-EL-1 | Electron 사이드카 수명주기 | M8 | todo | - | e2e 사이드카 | - |
| R-EL-2 | printToPDF | M8 | todo | - | e2e pdf | - |
| R-CI-1 | GH Actions Win+macOS 매트릭스 | M9 | todo | - | ci.yml green | - |
| R-CI-2 | Playwright-electron E2E 6시나리오 | M9 | todo | - | e2e-desktop | - |
