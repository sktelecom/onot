# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.3]

### Security

- The XLSX parser now rejects decompression-bomb workbooks before parsing, guarding
  against a crafted upload that exhausts memory while the request still returns 200. It
  checks the ZIP central directory (entry count, total uncompressed size, and overall
  compression ratio) before openpyxl reads any payload, caps the number of Package Info
  rows scanned, and deduplicates packages during the scan so repeated rows do not
  accumulate. Reported and reproduced against 1.1.0 through 1.1.2 (GHSA-qcgh-vq3j-cm8w).

## [1.1.2] - 2026-07-02

### Fixed

- Parse errors now reference the uploaded file's own name instead of an internal
  temporary name.
- SPDX documents with a non-standard extension, and SPDX YAML, are now detected by
  content and parsed instead of being rejected by extension.
- Non-Excel zip uploads and Excel files missing required sheets now return a clear
  400 error instead of crashing with HTTP 500.
- Markdown and text notices now escape package names/versions and company fields,
  preventing table breakage and link injection.
- Missing or empty license information now raises a warning instead of passing
  silently.

### Added

- "Try a sample" loads a bundled example SBOM so first-time users can preview a
  notice without their own file.
- The file picker filters toward SBOM types, and upload/parse errors now carry a
  plain-language recovery hint.

### Changed

- Preview and download stay disabled until a file parses successfully, and an empty
  output-format selection now explains why downloads are unavailable.
- A cancelled PDF save is reported instead of appearing to do nothing.
- Muted UI text was darkened to meet WCAG AA contrast.
- Desktop: the sidecar no longer flashes a console window on Windows, its output is
  captured to a log file, the first-run health timeout is longer on Windows, and a
  failed start shows a Retry/Quit dialog naming the log instead of quitting silently.

## [1.1.1] - 2026-07-01

### Fixed

- Packaged desktop app showed a blank screen on Windows: the bundled frontend
  referenced assets by absolute path, which fails over `file://`. Assets are now
  emitted with relative paths so the renderer loads correctly (#68).
- Cleared High/Critical dependency advisories (electron, undici, form-data).

### Changed

- The app and generated notices are English-only for the global release; the Korean
  locale was removed.

## [1.1.0] - 2026-06-03

This release is a full rewrite of onot as a type-safe Python core with a React UI,
shipped as an installable desktop app. It is the successor to the 1.0.0 PyQt-based
generator.

### Added

- Python core that reads SPDX 2.x (JSON/YAML/Tag-Value/RDF), CycloneDX (JSON/XML),
  and Excel, with input format auto-detection.
- Output renderers for HTML, Text, Markdown, and PDF, in English and Korean.
- Bundled SPDX license texts so notices can be generated fully offline (air-gapped);
  optional `--online` mode fills in any missing texts.
- `onot` CLI (`generate`, `formats`, `version`) and a local API sidecar
  (`onot-sidecar`) exposing `/api/parse`, `/api/render`, and `/api/formats`.
- Electron desktop app (Windows `.exe`, macOS `.dmg`) with a drag-and-drop
  upload → preview → download flow; all processing stays local.
- Security CI based on the TrustedOSS DevSecOps guidance: secret scanning (Gitleaks),
  SAST (CodeQL, Semgrep), and SCA (CycloneDX SBOM + grype).
- Community health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`,
  issue/PR templates, and `CODEOWNERS`.

### Changed

- Upgraded the frontend toolchain to Vite 6 and Vitest 4, and the desktop runtime to
  Electron 42 (off the end-of-life Electron 33), resolving known advisories.
- Replaced the proprietary Black Duck scan in CI with the open-source DevSecOps stack.

## [1.0.0] - 2023-03-21

- Initial public release: PyQt-based desktop generator that produced OSS notices
  from SPDX documents.

[Unreleased]: https://github.com/sktelecom/onot/compare/v1.1.2...HEAD
[1.1.2]: https://github.com/sktelecom/onot/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/sktelecom/onot/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/sktelecom/onot/compare/1.0.0...v1.1.0
[1.0.0]: https://github.com/sktelecom/onot/releases/tag/1.0.0
