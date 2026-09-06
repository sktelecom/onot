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
bash scripts/gate.sh   # ruff + pytest (coverage ≥ 90) + frontend build/test + electron tests
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

### While Actions is unavailable here

GitHub Actions currently cannot start on this repository. Every workflow fails
within seconds without running a single step, so a red check on your PR is not a
verdict on your change. The branch protection rules that required those checks have
been lifted for now and will be restored once Actions works again.

Maintainers verify changes on a fork in the meantime — `haksungjang/onot`, which runs
the same `ci` and `security` workflows on its own runners. Nothing in them depends on
organization secrets, so the results carry over. If you are working on a fork of your
own, enable Actions there and the checks will run on your branches.

Please still run the checks above locally before opening a PR; that is what the
review leans on right now.

## Pull request guidelines

- **Branch** off `main` (e.g. `feat/...`, `fix/...`, `chore/...`, `docs/...`).
- **Keep changes focused.** One logical change per PR is easier to review.
- **Add tests** for new behavior and keep coverage at or above 90%.
- **Write in English.** Commit messages, PR titles, PR descriptions, code comments, and docs
  are all written in English so the project stays accessible to a global audience.
- **Commit messages** follow [Conventional Commits](https://www.conventionalcommits.org/),
  e.g. `feat(render): add Markdown table layout` or `fix(ingest): handle empty SPDX relationships`.
- **Update docs** (`README.md`, `docs/USER_GUIDE.md`) when behavior changes, and add a
  `CHANGELOG.md` entry under `[Unreleased]`.

## Reporting bugs and requesting features

Use the [issue templates](https://github.com/sktelecom/onot/issues/new/choose). For
security issues, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

## Releasing (maintainers)

Releases are tag-driven. Pushing a `v*` tag triggers `.github/workflows/release.yml`:

1. Bump `version` in `pyproject.toml`, `src/onot/__init__.py`,
   `frontend/package.json`, and `electron/package.json`, and add a `CHANGELOG.md`
   entry. Merge to `main`.
2. Tag and push, e.g. `git tag v1.1.0 && git push origin v1.1.0`.
3. The workflow builds the Windows/macOS installers and publishes a GitHub Release.
   Final tags (no hyphen) are also published to PyPI; pre-release tags
   (e.g. `v1.1.0-rc1`) build installers only.

PyPI publishing uses **token-less Trusted Publishing (OIDC)**. One-time setup on
PyPI: add a trusted publisher for this project with owner `sktelecom`, repository
`onot`, workflow `release.yml`, and environment `pypi`.

### Releasing while Actions is unavailable here

A tag pushed to this repository currently builds nothing, so the release runs on the
`haksungjang/onot` fork instead and uploads the assets back here. `release.yml`
accepts a `workflow_call` for exactly this: `owner`/`repo` retarget the GitHub
Release, `version` names the tag, `publish` gates the upload, and `PUBLISH_TOKEN`
carries write access to this repository. The fork holds only a thin caller
(`publish-upstream-release.yml` on its `ci/publish-dry-run` branch) that calls this
workflow at `@main`, so there is no second copy of the build to drift.

1. Bump the versions and add the `CHANGELOG.md` entry as above, and merge to `main`.
2. Sync the fork's `main` with this repository.
3. Run the caller from the fork, naming the tag:

   ```bash
   gh workflow run publish-upstream-release.yml --repo haksungjang/onot \
     --ref ci/publish-dry-run -f version=v1.2.0 -f publish=true
   ```

Do not push a `v*` tag here while this lasts. It only leaves a failed run. The tag is
created by the release itself.

**A security fix does not take this path until its advisory is published.** Step 2
syncs a public fork, which would hand the patch to everyone watching it. Develop the
fix in the temporary private fork GitHub creates alongside the draft advisory and
merge that fork's PR when the fix is ready. That merge lands the patch on `main`
here, and it is a precondition for publishing: GitHub will not publish an advisory
while a PR is still open on the temporary fork. Publish, then sync the fork and
release.

So the patch does sit on a public branch for the few minutes between the merge and
the publication, and GitHub's flow offers no way around it. Publish as soon as the
merge lands and keep that window short. The full procedure, with the commands, is in
[docs/SECURITY_ADVISORY_PROCESS.md](docs/SECURITY_ADVISORY_PROCESS.md).

Pushing to the fork's `ci/publish-dry-run` branch rehearses the same build without
uploading anything, which is the way to check a change to the release path.

One thing does not carry over: Trusted Publishing identifies a workflow by its entry
point, so an upload starting on the fork never matches the publisher registered here.
That path authenticates with a PyPI API token and gives up the PEP 740 provenance
that only a Trusted Publishing upload carries. Once Actions works here again, a tag
pushed to this repository publishes token-lessly with provenance, as described above.

## License

By contributing, you agree that your contributions are licensed under the
[Apache-2.0 License](LICENSE).
