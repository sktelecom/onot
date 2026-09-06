# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-09-06

### Security

- The XLSX resource-exhaustion fix described under 1.1.3 reaches users here. The 1.1.3
  artifacts were built from a source tree that predated it, so this is the first release
  that actually carries it (GHSA-qcgh-vq3j-cm8w).

### Added

- The desktop app follows the system theme and offers an explicit Light or Dark choice,
  which it remembers. Light mode was written but unreachable before, because the app
  pinned dark mode on the document element.
- The window opens straight away and says the local engine is starting, instead of leaving
  nothing on screen for up to 40 seconds on macOS and two minutes on Windows while the
  sidecar came up.
- An application menu, replacing Electron's default. It carries Open SBOM and Save Notice
  with their usual shortcuts, About, and links to the user guide, the release notes, the
  releases page and the issue tracker. Reload and the developer tools appear only in a
  development build. Checking for updates opens a page: the app still contacts nothing on
  its own.
- The window remembers its size, position and maximised state, has a minimum size, and
  takes the name of the open file as its title.
- Saving reports where the file went, with Show in folder.
- The parse summary breaks components down by license, and each warning is shown with a
  line saying what it means for the notice.
- The notice details can be remembered between runs, and the copyright holder, which the
  API already accepted, is now on screen.
- The preview can be expanded to the height of the window.
- HTML notices open with a table of contents and link both ways between a component and
  the license it falls under, with a way back to the top in a long notice. A notice with
  hundreds of components could previously only be read by scrolling.
- `onot --version`, alongside the existing `onot version` subcommand.
- `onot init` writes a commented `onot.yaml`. The configuration schema existed only as
  fields in the source.
- `onot generate --json` reports the written files and the warnings as JSON, and `--quiet`
  suppresses the warnings.
- Exit codes and worked examples in `onot --help` and the README, so the CLI can be wired
  into a pipeline without reading the source.
- `docs/DESIGN.md` records the design tokens, the contrast bar CI enforces, and the traps
  in the notice stylesheet and the preview frame that have already cost a fix each.

### Changed

- The brand colour moves from green to the indigo of the logo, so the logo, the app and the
  generated notice share one colour. Colours, radii and spacing are now design tokens
  rather than values repeated across components.
- Saving a notice is the primary action. The primary button used to be Generate preview,
  which is a step on the way rather than the thing anyone came for.
- Output formats read as HTML, Text, Markdown and PDF rather than as API identifiers.
- The three parts of the screen are numbered, and Settings is now Notice details.
- All three text formats head a license with `Name (SPDX-Id)` and mark deprecated ids.
  Previously the id appeared only in Markdown and the marker only in HTML.
- Notices record the version of onot that produced them.
- Warnings end with a count by kind, so a run over a large SBOM says what the hundreds of
  lines amount to.
- The user guide covers macOS as well as Windows, having been Windows-only.

### Fixed

- The text notice now lists each component's copyright. It carried only the name and
  license, while HTML and Markdown both carried a Copyright column, so a product shipping
  the text notice alone omitted a notice that MIT and BSD style licenses require to be
  retained.
- Notices render in the intended sans-serif face. The theme stylesheet was HTML-escaped
  into the document, and since `<style>` never decodes an entity, the quoted font names
  broke the whole declaration and every notice fell back to the default serif.
- Generated PDFs no longer waste pages. A keep-together rule was applied to license blocks
  that run past a page, pushing each to a fresh page; on the SPDX sample this cost two of
  seven pages.
- The desktop PDF matches the one the CLI produces: same page size, margins and numbered
  footer. It previously ignored the print stylesheet entirely.
- Saved notices carry the product name and a timestamp on every route. The desktop app
  could not read the filename the API chose, because a cross-origin response hides
  `Content-Disposition` unless the server exposes it, so every desktop save fell back to a
  generic name.
- Accessibility: the primary button, the drop zone border, and the notice footer and page
  numbers all meet WCAG AA contrast, where they measured 3.46:1, 1.9:1 and 3.54:1. The drop
  zone shows a focus indicator when reached by keyboard, having shown none at all.
  Checkboxes follow the app's theme rather than the system's. `prefers-reduced-motion` is
  honoured.
- Quitting while the engine is still starting no longer hangs the app on a retry dialog.

## [1.1.3]

### Security

- The XLSX parser now rejects decompression-bomb workbooks before parsing, guarding
  against a crafted upload that exhausts memory while the request still returns 200. It
  checks the ZIP central directory (entry count, total uncompressed size, and overall
  compression ratio) before openpyxl reads any payload, caps the number of Package Info
  rows scanned, and deduplicates packages during the scan so repeated rows do not
  accumulate. Reported and reproduced against 1.1.0 through 1.1.2 (GHSA-qcgh-vq3j-cm8w).

The published 1.1.3 artifacts do not contain that fix. The release was built from a
source tree that predated the merge, so the package on PyPI and the installers attached
to the release are still vulnerable despite carrying the version number. Upgrade to
1.2.0 instead.

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

[Unreleased]: https://github.com/sktelecom/onot/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/sktelecom/onot/compare/v1.1.3...v1.2.0
[1.1.3]: https://github.com/sktelecom/onot/compare/v1.1.2...v1.1.3
[1.1.2]: https://github.com/sktelecom/onot/compare/v1.1.1...v1.1.2
[1.1.1]: https://github.com/sktelecom/onot/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/sktelecom/onot/compare/1.0.0...v1.1.0
[1.0.0]: https://github.com/sktelecom/onot/releases/tag/1.0.0
