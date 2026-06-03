# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/sktelecom/onot/compare/1.0.0...HEAD
[1.0.0]: https://github.com/sktelecom/onot/releases/tag/1.0.0
