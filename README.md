# onot

[![Latest release](https://img.shields.io/github/v/release/sktelecom/onot?sort=semver)](https://github.com/sktelecom/onot/releases/latest)
[![Download for Windows](https://img.shields.io/badge/Download-Windows%20installer-0078D6?logo=windows&logoColor=white)](https://github.com/sktelecom/onot/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/sktelecom/onot/total)](https://github.com/sktelecom/onot/releases)

`onot` generates open source software notices (OSS Notice) from SBOM documents.
It reads [SPDX](https://spdx.dev) 2.x (JSON/YAML/Tag-Value/RDF),
[CycloneDX](https://cyclonedx.org) (JSON/XML), and Excel, and produces HTML, Text,
Markdown, and PDF notices. License texts are bundled, so it runs fully offline
(air-gapped) — your SBOM never leaves the machine. Jointly developed by Kakao and
SK telecom.

![onot app](docs/images/04-preview.png)

> Korean user guide / 사용 가이드: [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

## Download (desktop app)

No setup required. Grab the latest installer from
[Releases](https://github.com/sktelecom/onot/releases), open the app, and drop in an
SBOM file to preview and download a notice — Windows (`onot-Setup-x.y.z.exe`) and
macOS (`.dmg`).

The installers are unsigned. On first launch Windows SmartScreen may warn about an
"unknown publisher" — choose **More info → Run anyway**. On macOS, right-click the app
and choose **Open** to pass Gatekeeper.

## CLI

```bash
pip install -e ".[spdx,cyclonedx,excel,api]"

# SBOM (format auto-detected) → notices in multiple formats
onot generate -i sbom.spdx.json -f html -f markdown --output-dir ./output

#   -f/--format   html | text | markdown | pdf (repeatable)
#   --lang        ko | en
#   --config      onot.yaml (company info, etc.)
#   --online      fetch missing license texts remotely (offline by default)
#   --stdout      write a single text format to stdout

onot formats   # supported output formats
onot version
```

Input format is auto-detected by extension and content (including SPDX JSON vs.
CycloneDX JSON). PDF output needs `pip install ".[pdf]"` (WeasyPrint); the desktop app
uses a built-in converter.

## Local API (sidecar)

```bash
onot-sidecar --port 8765
# POST /api/parse    upload → parse result
# POST /api/render   upload + format/lang/company → notice
# GET  /api/formats, GET /healthz
```

## Desktop app (Electron)

```bash
pnpm -C frontend install && pnpm -C frontend build
pnpm -C electron install && pnpm -C electron start   # dev
pnpm -C electron run dist                            # package (.dmg/.exe/.AppImage)
```

Upload → preview → download. All processing is local; the SBOM never leaves the machine.

## Development

```bash
bash .claude/gate.sh   # lint + pytest (cov ≥ 90) + frontend build/test + electron sidecar test
```

Refresh license data with `python scripts/update_license_data.py` (bundles SPDX
license-list-data). Design and decision records live in `docs/2.0/`
(TRACEABILITY.md, DECISIONS.md).

## Maintainers

| Name | Company | Email |
|--|--|--|
| [Rogers](https://github.com/HyunMinH) (한현민) | Kakao | um4825@gmail.com |
| [Haksung](https://github.com/haksungjang) (장학성) | SK telecom | hakssung@gmail.com |

## License

[Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)
