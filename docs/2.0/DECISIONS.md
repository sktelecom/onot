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
