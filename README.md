# onot

`onot`은 SBOM 문서로부터 오픈소스 고지문(OSS Notice)을 자동 생성하는 도구입니다.
[SPDX](https://spdx.dev) 2.x(JSON/YAML/Tag-Value/RDF), [CycloneDX](https://cyclonedx.org)(JSON/XML),
Excel을 입력으로 받아 HTML, Text, Markdown, PDF 고지문을 만듭니다. Kakao와 SK telecom이 함께
개발하는 오픈소스 프로젝트입니다.

> 2.0 재작성: 타입 안전한 Python 코어(표준 SPDX 라이브러리 재사용) + CLI + 로컬 API + 설치형
> 데스크톱(Electron). 라이선스 전문을 번들해 **네트워크 없이(에어갭) 동작**합니다.

## 다운로드 (Windows)

개발 환경을 따로 꾸리지 않아도 됩니다. [Releases](https://github.com/sktelecom/onot/releases)
페이지에서 최신 `onot Setup x.y.z.exe`를 받아 실행하면 설치됩니다. 앱을 열고 SBOM 파일을
끌어다 놓으면 고지문을 미리 보고 내려받을 수 있습니다. 모든 처리는 로컬에서 이뤄지며 SBOM이
외부로 나가지 않습니다.

설치 파일에 코드 서명이 되어 있지 않아 첫 실행 때 Windows SmartScreen이 "알 수 없는 게시자"
경고를 띄울 수 있습니다. 이때 `추가 정보`를 누른 뒤 `실행`을 선택하면 설치가 진행됩니다.

macOS 사용자는 같은 Releases 페이지에서 `.dmg`를 받습니다. 서명이 없어 첫 실행 시
앱을 우클릭한 뒤 `열기`를 선택해야 Gatekeeper를 통과합니다.

## 설치 (개발용)

소스에서 직접 빌드하려는 경우입니다.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[spdx,cyclonedx,excel,api]"
```

## CLI

```bash
# SBOM(포맷 자동 감지) → 여러 포맷 고지문 생성
onot generate -i sbom.spdx.json -f html -f markdown --output-dir ./output

# 옵션
#   -f/--format       html | text | markdown | pdf (반복 지정 가능)
#   --lang            ko | en
#   --config          onot.yaml (회사 정보 등)
#   --online          번들에 없는 라이선스 전문을 원격 보충(기본은 오프라인)
#   --stdout          단일 텍스트 포맷을 표준출력으로

onot formats     # 지원 출력 포맷
onot version
```

입력 포맷은 확장자와 내용으로 자동 감지합니다(SPDX JSON과 CycloneDX JSON 구분 포함).
PDF는 `pip install ".[pdf]"`(WeasyPrint)가 필요하며, 데스크톱 앱에서는 내장 변환을 씁니다.

## 로컬 API (사이드카)

```bash
onot-sidecar --port 8765
# POST /api/parse   (업로드 → 파싱 결과)
# POST /api/render  (업로드 + 포맷/언어/회사 → 고지문)
# GET  /api/formats, GET /healthz
```

## 데스크톱 앱 (Electron)

```bash
pnpm -C frontend install && pnpm -C frontend build
pnpm -C electron install && pnpm -C electron start   # 개발 실행
pnpm -C electron run dist                            # 패키징(.dmg/.exe/.AppImage)
```

업로드 → 미리보기 → 다운로드. 모든 처리가 로컬에서 수행되어 SBOM이 외부로 나가지 않습니다.

## 개발

```bash
bash .claude/gate.sh   # lint + pytest(cov≥90) + frontend build/test + electron 사이드카 테스트
```

라이선스 데이터 갱신: `python scripts/update_license_data.py` (SPDX license-list-data 번들).
설계·결정 문서는 `docs/2.0/`(TRACEABILITY.md, DECISIONS.md) 참고. 1.x 코드는 제거됨(이력은 git history 참고, D-017).

## Maintainer

| Name | Company | Email |
|--|--|--|
| [Rogers](https://github.com/HyunMinH) (한현민) | Kakao | um4825@gmail.com |
| [Haksung](https://github.com/haksungjang) (장학성) | SK telecom | hakssung@gmail.com |

## License

[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)
