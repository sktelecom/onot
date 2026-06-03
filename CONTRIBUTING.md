# Contributing to onot

Thanks for your interest in contributing! onot is an open source project jointly
developed by Kakao and SK telecom. This guide explains how to set up your
environment and get a change merged.

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Project layout

onot is a Python core with a React UI packaged as an installable desktop app.

- `src/onot/` — Python core (parsing, license resolution, rendering, CLI, local API)
- `frontend/` — React + Vite UI (Vitest tests)
- `electron/` — Electron desktop shell (Playwright E2E)
- `tests/` — Python test suite
- `docs/` — user guide and design/decision records (`docs/2.0/`)

## Development setup

### Python core

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[spdx,cyclonedx,excel,api,pdf,dev]"
```

### Frontend & desktop

```bash
pnpm -C frontend install
pnpm -C electron install
```

## Running checks

Before opening a pull request, run the full quality gate:

```bash
bash .claude/gate.sh   # ruff + pytest (coverage ≥ 90) + frontend build/test + electron tests
```

Or run pieces individually:

```bash
ruff check src tests && ruff format --check src tests   # lint/format
pytest --cov=onot --cov-fail-under=90                   # Python tests
pnpm -C frontend test                                   # UI unit tests
pnpm -C electron test                                   # sidecar lifecycle tests
```

CI runs the same checks on Linux, macOS, and Windows across Python 3.11–3.13, plus
SAST (CodeQL, Semgrep), SCA (SBOM + grype), and secret scanning. All checks must
pass before a PR can be merged.

## Pull request guidelines

- **Branch** off `main` (e.g. `feat/...`, `fix/...`, `chore/...`, `docs/...`).
- **Keep changes focused.** One logical change per PR is easier to review.
- **Add tests** for new behavior and keep coverage at or above 90%.
- **Commit messages** follow [Conventional Commits](https://www.conventionalcommits.org/),
  e.g. `feat(render): add Markdown table layout` or `fix(ingest): handle empty SPDX relationships`.
- **Update docs** (`README.md`, `docs/USER_GUIDE.md`) when behavior changes, and add a
  `CHANGELOG.md` entry under `[Unreleased]`.

## Reporting bugs and requesting features

Use the [issue templates](https://github.com/sktelecom/onot/issues/new/choose). For
security issues, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

## License

By contributing, you agree that your contributions are licensed under the
[Apache-2.0 License](LICENSE).
