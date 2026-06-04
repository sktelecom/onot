# onot 2.0 결정 로그 (ADR)

경량 ADR. 계획과 다른 선택, 스파이크 결론, deferred 항목을 결정과 근거 중심으로 기록한다.
형식: ID / 결정 / 근거 / 영향. 별도 표기가 없으면 날짜는 2026-06-02이며, 구현 상세와 검증
이력은 각 PR과 git history를 참조한다.

---

## D-001 — 의존성 도구를 uv 대신 venv+pip로

- **결정**: 1차 재현 환경은 표준 `python -m venv` + `pip` + 핀 고정으로 구성한다. `uv` 도입은 선택.
- **근거**: 작업 머신에 `uv`가 없고, 표준 도구만으로 외부 설치 없이 즉시 재현하고 이식성을 확보한다.
- **영향**: 플랜 §9.6, gate.sh.

## D-002 — 신규 코드는 src-layout(`src/onot/`)로 1.x와 평행 구축

- **결정**: 2.0 코어는 `src/onot/`에 신설하고, 1.x는 `legacy/onot/`로 옮겨 import 경로를 분리한다(삭제는 후속 결정).
- **근거**: 평행 구축으로 통합 리스크와 롤백 안전을 확보하고, 루트 `onot/`가 `import onot`을 가리는 그림자를 제거한다.
- **영향**: 패키지 레이아웃, 최종 수용 기준. (제거는 D-017에서 확정)

## D-003 — 2.0 작업 브랜치 베이스는 main

- **결정**: 마일스톤 브랜치는 최신 `main`에서 분기한다(`feat/2.0-m<N>-<slug>`). `main` 직접 커밋 금지는 유지.
- **근거**: 최신 커밋이 `main`에 있고 `origin/dev`는 뒤처져, 최신 베이스라인 위에서 작업해 충돌을 줄인다.
- **영향**: 플랜 §9.6 브랜치 전략.

## D-004 — S1: license-expression / spdx-tools API 확정

- **결정**: 두 라이브러리의 표현식 파싱과 SPDX 2.x 문서 모델을 M2/M3 매핑의 기반으로 채택한다(API 검증 완료).
- **근거**: 중첩 OR/AND와 WITH 예외가 정확히 평탄화되고, `GPL-2.0+`는 `GPL-2.0-or-later`로 정규화되며,
  unknown 심볼은 `licensing.validate(...).errors`로 검출된다. 플랜 §2, §3 가정 유효. 근거: `spikes/s1_license_spdx/`.
- **영향**: M2 expression_parser/resolver, M3 SpdxAdapter.

## D-005 — SPDX 3.0 입력은 후속으로 분리 (deferred)

- **결정**: 1차 입력은 SPDX 2.x(JSON/YAML/Tag-Value/RDF), CycloneDX, Excel. SPDX 3.0 입력은 후속으로 분리한다.
- **근거**: spdx-tools 0.8.5에 `spdx3.parser`가 없어 3.0 문서를 파싱할 수 없다. 라이브러리 성숙 시 재개.
- **영향**: 플랜 §2, TRACEABILITY R-S2/R-ING-1.

## D-006 — frozen 리소스 접근은 '/' 체이닝 (다중 인자 joinpath 금지)

- **결정**: 번들 데이터는 항상 `files("onot.license") / "data" / "licenses.json"`처럼 `/` 체이닝으로 접근한다.
  PyInstaller 빌드 시 `--add-data`/`--collect-data`로 동봉.
- **근거**: frozen에서 `files(pkg)`가 `MultiplexedPath`를 반환해 다중 인자 `joinpath`가 `TypeError`를 낸다(비-frozen은 정상). 근거: `spikes/s3_frozen/`.
- **영향**: M2 catalog.py, M8 사이드카 빌드. 에어갭 요건 핵심 리스크 해소.

## D-007 — 기존 sample/ 은 spec-호환 SPDX가 아님 → 실 SBOM 픽스처 사용

- **결정**: SPDX 어댑터 테스트는 syft/cdxgen 등이 생성한 spec-호환 픽스처를 `tests/fixtures/sbom/`에 별도 마련한다. ExcelAdapter만 1.x 템플릿 xlsx를 계속 처리.
- **근거**: 기존 `sample/`의 rdf/xlsx는 1.x 전용 예제로 spec 파싱에 실패한다.
- **영향**: M3 픽스처, TRACEABILITY R-ING-1.

## D-008 — S4(Electron 사이드카)·S5(PDF) 스파이크는 M8 시작 시 수행

- **결정**: Electron 툴체인이 필요한 S4/S5 스파이크를 M8 첫 작업으로 시퀀싱한다.
- **근거**: M1~M7이 여기에 의존하지 않고, 사이드카의 frozen 리소스 리스크는 S3에서 이미 해소됐다. "빌드 전 검증" 원칙 충족.
- **영향**: 플랜 §9.5, TRACEABILITY R-S4/R-S5.

## D-009 — 게이트 정책: M1부터 L1+L2+L3 3중 게이트

- **결정**: M0.5(골격 슬라이스)는 L1+L3으로 종료하고, gate-verifier(L2)를 포함한 3중 게이트는 M1부터 전면 적용한다.
- **근거**: M0.5는 acceptance 9.9의 M1~M9에 포함되지 않는 골격 단계다.
- **영향**: 플랜 §9.1.

## D-010 — M2 라이선스 레이어: 번들과 정규화

- **결정**: SPDX license-list-data v3.28.0(727 licenses + 84 exceptions, 전문 포함)을 `src/onot/license/data/licenses.json`
  단일 파일로 vendoring한다(`scripts/update_license_data.py`). deprecated SPDX id는 canonical로 정규화해 채택.
- **근거**: 에어갭에서 네트워크 없이 전문을 채우기 위함. 정규화는 고지문 품질에 유리. online fetch는 SPDX id 화이트리스트로 제한해 URL 인젝션을 차단.
- **영향**: 플랜 §3, M4 렌더러.

## D-011 — M3 ingest: 4 어댑터와 자동감지, XML 보안

- **결정**: SpdxAdapter(2.x), CycloneDxAdapter(JSON/XML), ExcelAdapter를 두고 detect/registry가 확장자와 내용 스니핑으로 라우팅한다(.json 모호성은 내용으로 해소).
- **근거**: regex 가드가 UTF-16/32 인코딩으로 우회되어, `_xml_guard`가 원본과 다중 인코딩 디코딩본을 함께 검사하도록 강화했다(CDX는 defusedxml 2차 방어). CDX named 라이선스 slug 충돌은 suffix 분리로 해소.
- **영향**: 플랜 §2, M4 렌더러.

## D-012 — M4 렌더링: 4 렌더러, i18n, 테마

- **결정**: Renderer ABC 아래 Html/Text/Markdown/Pdf. Jinja2 autoescape(HTML), 테마 CSS 분리, i18n은 en/ko YAML 카탈로그.
  PDF는 web/CLI에서 WeasyPrint, 설치형은 Electron printToPDF(M8).
- **근거**: license_links substring 치환이 "MIT"를 "MITNFA" 내부에서 다시 치환하는 clobber가 있어 정규식 토큰화로 교체. i18n 카탈로그는 불변(MappingProxyType)으로 보호.
- **영향**: 플랜 §4, §5, M5 CLI.

## D-013 — M5 CLI: 다중 포맷, 자동감지, 종료 코드

- **결정**: `generate`(다중 `-f`, `--output-dir`, `--lang`, `--config`, `--offline/--online`, `--strict`, `--stdout`),
  `formats`, `version`. 종료 코드는 IngestError=2, LicenseError=3, ConfigError=4, 기타=1.
- **근거**: unknown 포맷은 사전 검증으로 클린 메시지를 내고, `--online`은 RemoteLicenseFetcher + DiskCache를 주입한다. 설정 우선순위는 CLI > yaml > env > 기본.
- **영향**: 플랜 §6.4. M6 API가 동일 코어를 재사용.

## D-014 — M6 FastAPI 사이드카

- **결정**: `/healthz`, `/api/formats`, `POST /api/parse`, `POST /api/render`를 CLI와 동일 코어로 제공한다. stateless로
  업로드를 임시파일에서 처리 후 폐기. CORS는 localhost/127.0.0.1만 허용.
- **근거**: 파일명은 suffix만 사용해 traversal을 막고, XXE 업로드는 ingest 가드로 400, 한도 초과는 413. OnotError를 HTTP로 매핑(Ingest 400, License 422, 기타 500).
- **영향**: 플랜 §6.2. M7 프론트, M8 Electron이 사용.

## D-015 — M7 React 프론트엔드

- **결정**: Vite + React 18 + TypeScript(strict) + Tailwind. shadcn 스타일 컴포넌트를 직접 작성하고 Radix는 도입하지 않는다(경량화). 미리보기 iframe은 `sandbox=""`.
- **근거**: 의존성을 줄이고, iframe sandbox로 미리보기 스크립트를 차단해 백엔드 autoescape와 2중 방어를 둔다. 다운로드 파일명은 Content-Disposition을 파싱해 백엔드 값을 사용.
- **영향**: 플랜 §6.1. M8 Electron이 정적 빌드를 로드.

## D-016 — M8 Electron 셸 + S4/S5 결과

- **결정**: 데스크톱 PDF는 Electron `printToPDF`(격리 오프스크린 창, `javascript:false`)로 하고 WeasyPrint는 사이드카에 번들하지 않는다. 사이드카 수명주기는 순수 Node 매니저(findFreePort → spawn → /healthz 폴링 → SIGTERM→SIGKILL)로 관리.
- **근거**: S4에서 PyInstaller `--collect-all`로 빌드한 `onot-sidecar`가 파싱과 에어갭 HTML 렌더, 클린 종료까지 실증.
  WeasyPrint(GTK)는 무거워 제외. 첫 기동은 macOS Gatekeeper 스캔으로 느려 start 타임아웃 40s. 외부 링크는 시스템 브라우저로 위임.
- **영향**: 플랜 §6.3, §9.5. M9 CI 패키징/E2E.

## D-017 — M9 CI + 1.x legacy 제거

- **결정(CI)**: 1.x `python-app.yml`을 `.github/workflows/ci.yml`로 교체한다. lint(ruff), test-core(ubuntu/windows/macos × py3.11–3.13, cov≥90),
  test-pdf, frontend(build+vitest), build-desktop(electron-builder + PyInstaller 사이드카), e2e-desktop(Playwright-electron).
- **결정(보안 CI)**: 상용 Black Duck Detect를 제거하고 [TrustedOSS DevSecOps](https://trustedoss.github.io/devsecops/intro) 권장
  오픈소스 스택으로 대체한다. Gitleaks(secret), Semgrep과 CodeQL(SAST, CodeQL은 주간 cron), anchore sbom-action + grype(SCA, High 이상 차단).
  대상이 없는 컨테이너(Trivy), IaC(Checkov), DAST(ZAP)는 제외.
- **결정(legacy)**: 1.x 잔재를 완전 제거한다. 대상은 `legacy/onot/`, `legacy/test/`, 루트 `setup.py`, `requirements.txt`,
  1.x 산출물 `output/`, Excel 샘플 `sample/`과 `docs/how_to_prepare.md`, README의 legacy 언급.
- **근거**: 이력은 git history로 추적 가능하고, src-layout과의 그림자 위험과 리포 혼란을 없애는 편이 보존 이득보다 크다.
- **영향**: 플랜 §8.4, 최종 수용 기준.
