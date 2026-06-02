# onot 2.0 결정 로그 (ADR)

경량 ADR. 계획과 다른 모든 선택, 스파이크 결론, deferred 항목을 여기에 기록한다.
형식: ID / 날짜 / 컨텍스트 / 결정 / 근거 / 영향.

---

## D-001 — 의존성 도구를 uv 대신 venv+pip로

- **날짜**: 2026-06-02
- **컨텍스트**: 플랜 §9.6은 `uv.lock` 기반 재현 환경을 권장하나, 작업 머신에 `uv`가 설치돼 있지 않다(확인: `uv --version` → not found). Python 3.11.15 존재.
- **결정**: 1차는 표준 `python -m venv` + `pip` + 핀 고정(`requirements/*.txt` 또는 `pip freeze` 스냅샷)으로 재현 환경을 구성한다. 추후 `uv` 도입은 선택.
- **근거**: 외부 도구 설치 없이 즉시 재현 가능, 표준 도구로 이식성 확보.
- **영향**: §9.6 재현 환경, gate.sh.

## D-002 — 신규 코드는 src-layout(`src/onot/`)로 기존 1.x와 평행 구축

- **날짜**: 2026-06-02
- **컨텍스트**: 공식 onot 대체(브레이킹 허용)지만, 안전한 롤백을 위해 1.x(`onot/` 평면 패키지)를 즉시 제거하지 않는다.
- **결정**: 2.0 코어는 `src/onot/`(src-layout)에 신설한다. 리포 루트의 1.x `onot/`가 `import onot`을 가리는 그림자 문제가 있어 1.x를 `legacy/onot/`로, 구 테스트를 `legacy/test/`로 이동해 참조용으로 보존한다(삭제 아님). M9 종료 시점에 `legacy/` 제거 또는 보존을 명시 결정한다.
- **근거**: 평행 구축으로 통합 리스크와 롤백 안전 확보. 1.x를 import 경로에서 분리해 그림자 제거. pyproject는 src만 패키징하므로 충돌 없음.
- **영향**: 패키지 레이아웃, 최종 수용 기준(1.x 잔재 처리).

## D-003 — 2.0 작업 브랜치 베이스는 main

- **날짜**: 2026-06-02
- **컨텍스트**: §9.6은 베이스 `dev`를 제시하나 최신 커밋(#21 Black Duck, #22 Windows 인코딩)은 `main`에 있고 `origin/dev`는 뒤처졌을 수 있다.
- **결정**: 2.0 마일스톤 브랜치는 최신 `main`에서 분기한다(`feat/2.0-m<N>-<slug>`). `main` 직접 커밋 금지 규칙은 유지. 통합 누적 브랜치는 추후 필요 시 `dev`를 main 기준으로 재설정.
- **근거**: 최신 베이스라인 위에서 작업해 중복/충돌 최소화.
- **영향**: §9.6 브랜치 전략.

## D-004 — S1 PASS: license-expression / spdx-tools API 확정

- **날짜**: 2026-06-02 / **근거**: `spikes/s1_license_spdx/spike.py`
- **결정/확정 사실**:
  - `get_spdx_licensing().parse(expr)` + `license_symbols(parsed, unique=True, decompose=True)`가 중첩 `OR/AND`, `WITH` 예외를 정확히 평탄화. `WITH`는 license와 exception 심볼을 분리 노출.
  - `GPL-2.0+`는 `GPL-2.0-or-later`로 정규화됨.
  - unknown 심볼은 `licensing.validate(expr).errors`(예: `Unknown license key(s): ...`)로 검출. (`unknown_license_keys` 같은 별도 필드 아님)
  - spdx-tools `parse_anything.parse_file()` → `Document`. `doc.creation_info`(name, spdx_version, creators[Actor]), `doc.packages[*]`(name, version, `license_concluded`/`license_declared`는 str()로 표현식 문자열, copyright_text, download_location), `doc.extracted_licensing_info`. `validate_full_spdx_document()`는 메시지 리스트(유효 시 0).
- **영향**: M2 expression_parser/resolver, M3 SpdxAdapter 매핑. 플랜 §2·§3 가정 유효.

## D-005 — SPDX 3.0 입력은 후속으로 분리(1차 제외)

- **날짜**: 2026-06-02 / **근거**: `spikes/s2_s3 probe`
- **컨텍스트**: spdx-tools 0.8.5는 `spdx_tools.spdx3.model`은 제공하나 `spdx_tools.spdx3.parser`가 없다 → 3.0 문서 파싱 불가.
- **결정**: 1차 입력 포맷은 SPDX 2.x(JSON/YAML/Tag-Value/RDF) + CycloneDX + Excel. **SPDX 3.0 입력은 후속 단계로 분리**(deferred). 라이브러리 3.0 파서 성숙 또는 `spdx-python-model` 도입 시 재개.
- **영향**: 플랜 §2 입력 포맷, TRACEABILITY R-S2/R-ING-1(3.0 부분).

## D-006 — frozen 리소스 접근은 '/' 체이닝(다중 인자 joinpath 금지)

- **날짜**: 2026-06-02 / **근거**: `spikes/s3_frozen/`(PyInstaller 6.20 onefile 빌드·실행 PASS)
- **컨텍스트**: PyInstaller frozen에서 `importlib.resources.files(pkg)`가 `MultiplexedPath`를 반환하며, `joinpath("a","b")`(다중 인자)는 `TypeError`. 비-frozen(editable)에서는 정상.
- **결정**: 번들 데이터 접근은 항상 `files("onot.license") / "data" / "licenses.json"`처럼 `/` 체이닝으로 작성한다. PyInstaller 빌드 시 `--add-data`(또는 `--collect-data onot`)로 데이터 동봉. 에어갭 번들 접근 패턴 확정.
- **영향**: M2 catalog.py, M8 사이드카 빌드. 에어갭 1급 요건 핵심 리스크 해소.

## D-007 — 기존 sample/ 은 spec-호환 SPDX가 아님 → M3는 실 SBOM 픽스처 필요

- **날짜**: 2026-06-02 / **근거**: S1에서 `sample/SPDXRdfExample-v2.3.rdf.xml` 파싱 실패(`Actor "SourceDownloadUrl: ..." 불일치`)
- **결정**: 기존 `sample/` xlsx·rdf는 1.x onot 전용 예제다. SPDX 어댑터 테스트에는 syft/cdxgen 등이 생성한 spec-호환 SPDX 픽스처를 별도 마련한다(`tests/fixtures/sbom/`). 단, ExcelAdapter는 1.x 템플릿 xlsx를 입력으로 계속 처리(별 경로).
- **영향**: M3 픽스처, TRACEABILITY R-ING-1.

## D-008 — S4(Electron 사이드카)·S5(PDF) 스파이크는 M8 직전 블록으로 시퀀싱

- **날짜**: 2026-06-02
- **컨텍스트**: S4/S5는 Electron 툴체인(대용량 npm)이 필요하나 M1~M7 어느 것도 여기에 의존하지 않는다. 사이드카의 Python측 패키징 리스크(frozen + 리소스 접근)는 S3에서 이미 해소.
- **결정**: S4(Electron이 frozen FastAPI 사이드카를 spawn→health→graceful kill, Win/mac)와 S5(printToPDF vs 서버사이드)를 **M8 시작 시 첫 작업으로** 수행한다. "그 위에 빌드하기 전에 검증" 원칙은 유지(M1~M7이 의존하지 않으므로 충족).
- **영향**: 플랜 §9.5 스파이크 순서. TRACEABILITY R-S4/R-S5 = sequenced(M8). 사일런트 컷 아님(표면화).

## D-009 — M0.5 수직 슬라이스 L3 리뷰 반영

- **날짜**: 2026-06-02 / **근거**: code-reviewer(L3) CHANGE_REQUESTED
- **결정**: blocking 1건(ExcelAdapter 짧은 행 IndexError)을 `_cell()` 안전 접근 + 회귀 테스트(`tests/ingest/test_excel_robust.py`)로 해소. 고가치 advisory 반영 — 파이프라인 결정성 테스트 강화(#3), effective_expression 독립 단언(#4), `_symbols` 폴백 단위(#2), naming docstring 정정(#7).
- **보류(advisory)**: #6 슬라이스 전용 픽스처 독립화 → M3에서 spec-호환 SBOM 픽스처 도입 시 함께(D-007). 현재는 안정적 커밋 자산 `sample/`에 골든을 묶음(수용).
- **게이트 적용 범위**: M0.5는 acceptance 9.9의 M1~M9에 포함되지 않는 골격 슬라이스라 L1(green 96%)+L3(반영)로 종료. **전면 3중 게이트(L2 gate-verifier 포함)는 M1부터 적용**.
- **영향**: §9.1 게이트, M3 픽스처.

## D-010 — M2 라이선스 레이어: 번들·정규화·게이트

- **날짜**: 2026-06-02 / **근거**: M2 3중 게이트
- **번들**: SPDX license-list-data **v3.28.0**(727 licenses + 84 exceptions, 전문 포함, 5.0MB)을 `src/onot/license/data/licenses.json` 단일 파일로 vendoring(`scripts/update_license_data.py`). 에어갭에서 NETWORK=0으로 전문 채움(L2 실증).
- **정규화 발견**: license-expression은 deprecated SPDX id(예: `GPL-2.0`)를 canonical(`GPL-2.0-only`)로 정규화한다. 고지문 품질에 유리하므로 그대로 채택. deprecated/reference 전파는 catalog→License 경로로 직접 테스트.
- **L3 blocking 해소**: fetcher가 `httpx.InvalidURL` 미처리 → 깨진 표현식이 online fetch로 흘러 resolve 크래시. SPDX id 화이트리스트(`[A-Za-z0-9.+-]+`) + InvalidURL catch로 해소(회귀 테스트 `test_invalid_id_returns_none_without_network`). 보안(URL 인젝션)도 함께 차단.
- **3중 게이트**: L1 green(74 테스트, cov 98.5%, 임계 90), L2 PASS(위장 0, 에어갭 실증), L3 blocking 해소. advisory도 반영했다 — deprecated 전파, 빈 텍스트 폴백, offline 무fetch, fetcher close 주석.
- **골든 변경**: License.text가 번들 전문으로 채워져 슬라이스 골든이 4.5KB→121KB(전문 포함, 에어갭 고지문). 의도된 M2 산출.
- **영향**: §3 라이선스, M4 렌더러(deprecated/reference_url 사용).

## D-011 — M3 ingest: 4 어댑터·자동감지·XML 보안

- **날짜**: 2026-06-02 / **근거**: M3 3중 게이트
- **어댑터**: SpdxAdapter(spdx-tools, 2.x), CycloneDxAdapter(JSON/XML, cyclonedx-python-lib), ExcelAdapter. detect/registry가 확장자+내용 스니핑으로 라우팅(.json 모호성은 내용으로 해소). 픽스처는 spec 호환 SBOM 신규 작성(D-007).
- **XML 보안(L3 blocking 2건 해소)**:
  - regex 가드가 UTF-16/32 인코딩으로 우회되던 문제 → `_xml_guard`가 원본+null제거본+다중 인코딩 디코딩본을 함께 검사하도록 강화. CDX는 defusedxml 2차 방어, SPDX RDF는 강화된 가드가 단일 방어(회귀 테스트 포함).
  - defusedxml 거부를 IngestValidationError로 분류(의미 보존).
- **정확성(L3 blocking 해소)**: CDX named 라이선스 slug 충돌 시 LicenseRef 무음 덮어쓰기 → 충돌 감지 + suffix 분리(`_register_named_ref`), 동일 name+text는 dedup.
- **3중 게이트**: L1 green(101 테스트, cov 96.9%, 임계 90), L2 PASS(XXE 실증, 위장 0), L3 blocking 2건 해소.
- **영향**: §2 입력 어댑터, M4 렌더러.

## D-012 — M4 core+rendering: 4 렌더러, i18n, 테마, config

- **날짜**: 2026-06-02 / **근거**: M4 3중 게이트
- **렌더링**: Renderer ABC → TemplateRenderer → Html/Text/Markdown/Pdf. Jinja2 autoescape(HTML), 테마 CSS 분리, license_links 앵커(토큰화), context 병합(회사>SBOM), i18n(en/ko YAML 카탈로그). PDF는 WeasyPrint extras(설치형은 Electron printToPDF=M8). 골든 html/text/md 재생성.
- **L1 버그(테스트가 잡음)**: license_links substring 치환이 "MIT"를 "MITNFA" 링크 내부에서 또 치환하는 clobber → 정규식 토큰화로 교체.
- **L3 advisory 보완**: i18n 카탈로그 MappingProxyType(불변)+플레이스홀더 불일치 방어적 포맷, markdown md_code_block(백틱 런보다 긴 펜스로 fence 탈출 방지), OutputWriter 테스트 추가, 전 언어·전 포맷 풀렌더 테스트(플레이스홀더 키 커버), 미사용 M0.5 템플릿 제거.
- **3중 게이트**: L1 green(134 테스트, cov 96.1%, 임계 90), L2 PASS(이스케이프·i18n·골든 실증, 위장 0), L3 blocking 0 + advisory 보완.
- **영향**: §4 렌더링, §5 i18n, M5 CLI(다중 포맷 연결).

## D-013 — M5 CLI: 다중 포맷·자동감지·종료 코드

- **날짜**: 2026-06-02 / **근거**: M5 3중 게이트
- **CLI**: generate(다중 -f, --output-dir, --lang, --config yaml, --offline/--online, --strict, --stdout), formats, version. load_document 자동감지 → LicenseResolver → 각 포맷 render → OutputWriter. 파일명에 timestamp.
- **종료 코드**: IngestError=2, LicenseError=3, ConfigError=4, 기타=1.
- **L3 blocking 2건 해소**:
  - unknown --format이 ValueError로 트레이스백 노출 → is_supported로 사전 검증 후 클린 메시지 + exit 2(별칭 txt/md 포함). 중복 포맷 dedup.
  - --online이 무동작(fetcher 미주입) → 온라인 시 RemoteLicenseFetcher + DiskCache(버전 네임스페이스) 주입. ConfigError→4 매핑 추가.
- **L3 advisory 보완**: load_settings가 CLI 오버라이드를 yaml 위에 병합 후 Settings로 재검증(잘못된 lang → ConfigError → exit 4), 설정 우선순위 docstring 정정(CLI>yaml>env>기본).
- **3중 게이트**: L1 green(148 테스트, cov 96.2%, 임계 90), L2 PASS, L3 blocking 2건 해소.
- **영향**: §6.4 CLI. M6 API가 동일 코어 오케스트레이션 재사용.

## D-014 — M6 FastAPI 사이드카

- **날짜**: 2026-06-02 / **근거**: M6 3중 게이트
- **API**: healthz, /api/formats, POST /api/parse(업로드→도메인 문서+경고), POST /api/render(업로드+포맷/언어/회사→산출물). CLI와 동일 코어(ingest 자동감지→resolver→render) 재사용. stateless: 업로드를 임시파일로 받아 처리 후 폐기.
- **보안(L2 실증)**: 파일명은 suffix만 사용(traversal 차단), tempfile 시스템 생성, XXE 업로드는 ingest 가드로 400, 빈 400, 미지원 400, 대용량 413. OnotError→HTTP(IngestError 400, LicenseError 422, 기타 500). Content-Disposition 파일명은 slug라 헤더 주입 불가. CORS는 localhost/127.0.0.1만(Starlette fullmatch).
- **L3 advisory 보완**: 중복 get_renderer 제거(download 시에만), render 경로 XXE 테스트, _http_error 매핑 단위 테스트(422/500 커버), XXE detail 단언, PDF render 테스트(importorskip).
- **수용한 advisory**: 업로드를 메모리에 읽은 뒤 크기 체크(청크 조기거절 아님) — 127.0.0.1 단일 사용자 사이드카 + 25MB 한도라 수용. 향후 호스팅 SaaS 시 청크 검사 재검토.
- **3중 게이트**: L1 green(170 테스트+2 skip, cov 96.5%, routes 100%, 임계 90), L2 PASS, L3 blocking 0.
- **영향**: §6.2 API. M7 프론트가 이 API 호출, M8 Electron이 사이드카로 기동.

## D-015 — M7 React 프론트엔드

- **날짜**: 2026-06-02 / **근거**: M7 3중 게이트
- **스택**: Vite + React 18 + TypeScript(strict) + Tailwind. shadcn 스타일 컴포넌트(Button/Card) 직접 작성(Radix 미도입, 의존성 경량화). lucide 아이콘. M6 FastAPI 호출.
- **플로우**: 드래그앤드롭 업로드 → /api/parse(패키지 수·경고 표시) → 설정(포맷/언어/회사) → 미리보기(iframe srcDoc sandbox="") → 다운로드. 다국어 UI(en/ko), 다크모드.
- **보안**: 미리보기 iframe `sandbox=""`로 스크립트 차단(L3 확인), 에러 detail은 React 기본 이스케이프. 백엔드 autoescape와 2중 방어.
- **테스트**: vitest 21개 — API 클라이언트(fetch mock), 컴포넌트(FileDropzone/SettingsPanel), App 플로우, a11y(axe 0 위반), i18n 파리티, 다운로드 경로.
- **L3 blocking 2건 해소**: ① 다운로드 파일명이 클라이언트 하드코딩으로 백엔드 제품명 파일명을 덮어씀 → Content-Disposition 파싱해 백엔드 파일명 사용 ② revokeObjectURL 동기 호출 + 앵커 미append 경쟁 → append+click+remove+setTimeout 해제. 회귀 테스트 포함.
- **L3 advisory 보완**: detail 비문자열 방어, parsing/noFile 상태 노출.
- **gate.sh 진화(M7)**: pytest + `pnpm -C frontend build && test` 추가.
- **3중 게이트**: L1 green(Python 170 + 프론트 21, 빌드 OK), L2 PASS(axe·파리티·빌드 실증), L3 blocking 2건 해소.
- **영향**: §6.1 프론트. M8 Electron이 이 정적 빌드를 로드 + 사이드카 기동.

## D-016 — M8 Electron 셸 + S4/S5 스파이크 결과

- **날짜**: 2026-06-02 / **근거**: M8 3중 게이트 + S4/S5 스파이크
- **S4 PASS(frozen 사이드카 수명주기)**: PyInstaller `--collect-all`(onot/uvicorn/spdx_tools/cyclonedx/license_expression/openpyxl/defusedxml)로 빌드한 `onot-sidecar`(53MB onedir)가 SPDX/CycloneDX/Excel 파싱 + HTML 렌더(번들 전문, 에어갭) + 클린 종료까지 실증. 지연 import도 번들됨. 첫 기동은 macOS Gatekeeper 스캔으로 느림(최대 ~30s) → start 타임아웃 40s.
- **S5 결정(PDF)**: 데스크톱 PDF = Electron `printToPDF`(격리 오프스크린 창, `javascript:false`). 사이드카에 WeasyPrint(무거운 GTK) 미번들. 프론트는 Electron(window.onot.exportPdf) 감지 시 HTML 렌더 후 printToPDF, 웹/CLI는 WeasyPrint extras.
- **사이드카 수명주기 매니저**(electron/lib/sidecar.mjs, 순수 Node): findFreePort → spawn → /healthz 폴링 → SIGTERM→SIGKILL graceful. node:test로 spawn→health→stop→고아 없음 검증(gate.sh M8).
- **L3 blocking 3건 해소**: ① 메인 윈도우 네비게이션/window-open 가드(외부 링크는 시스템 브라우저) ② printToPDF 오프스크린 창 명시 격리(nodeIntegration off, contextIsolation, sandbox, javascript off) ③ 종료 경합 → 멱등 shutdown promise로 단일화. 추가: whenReady catch(기동 실패 시 종료), CSP, IPC 입력 검증, findFreePort 테스트 실바인드.
- **위임(M9 CI)**: 실제 Electron 기동 + Playwright-electron E2E, electron-builder 패키징(.dmg/.exe), Win/mac 매트릭스, 코드 서명/공증(D-008, electron-builder.yml에 미서명 명시).
- **3중 게이트**: L1 green(Python 170 + 프론트 24 + electron 2), L2 PASS(실증 4 PASS, 위임 표면화), L3 blocking 3건 해소.
- **영향**: §6.3 Electron, §9.5 S4/S5 스파이크. M9 CI 패키징·E2E.

## D-017 — M9 CI + 1.x legacy 보존

- **날짜**: 2026-06-02 / **근거**: M9
- **CI(`.github/workflows/ci.yml`)**: 1.x `python-app.yml`(py3.8, PyQt exe, flake8 오타)을 교체. 잡: lint(ruff), test-core(ubuntu/windows/macos × py3.11–3.13, cov≥90), test-pdf(ubuntu+pango), frontend(build+vitest), build-desktop(win/mac electron-builder + PyInstaller 사이드카), e2e-desktop(win/mac, node 사이드카 테스트 + Playwright-electron), security(Black Duck Detect, secrets 있을 때만). secrets는 if에서 직접 못 쓰므로 env 경유.
- **Playwright-electron E2E**(electron/e2e/app.e2e.mjs): 실제 앱 기동 → 사이드카 파싱 → 미리보기 풀 플로우. CI(Win/mac)에서 실행. dev 사이드카 python은 `ONOT_SIDECAR_PYTHON`로 재정의(CI는 시스템 python).
- **1.x legacy 보존**: `legacy/onot/`·`legacy/test/`를 이번 릴리스에서 제거하지 않고 참조용으로 보존(import 경로 분리됨, src-layout과 충돌 없음). 완전 제거는 2.0 안정화 후 후속 결정. acceptance 9.9의 "1.x 잔재 처리"를 보존으로 명시 결정.
- **영향**: §8.4 CI, 최종 수용 기준.
- **갱신(2026-06-02, 보존→제거)**: 1.x 잔재를 완전 제거하기로 결정 변경. 제거 대상은 다음과 같다.
  - `legacy/onot/`, `legacy/test/`
  - 루트 `setup.py`, `requirements.txt`
  - 1.x 산출물 `output/`
  - 1.x용 Excel 샘플 `sample/`과 준비 가이드 `docs/how_to_prepare.md`

  이력은 git history로 충분히 추적할 수 있고, src-layout(`src/onot/`)과의 그림자 위험과 리포 혼란을 없애는 편이 보존 이득보다 크다고 판단했다. README의 legacy 언급도 함께 정리한다.
