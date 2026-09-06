# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""onot CLI entry point (Typer).

generate (multiple formats, auto-detection, language, settings), formats, version.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer

from onot import __version__
from onot.cli.warnings import summarize
from onot.core.config import load_settings
from onot.core.naming import output_filename
from onot.core.writer import OutputWriter
from onot.domain.errors import ConfigError, IngestError, LicenseError, OnotError
from onot.ingest import load_document
from onot.license.cache import DiskCache
from onot.license.catalog import SpdxLicenseCatalog
from onot.license.fetcher import RemoteLicenseFetcher
from onot.license.resolver import LicenseResolver
from onot.rendering import available_formats, get_renderer, render
from onot.rendering.registry import is_supported

# \b keeps click from reflowing the block that follows it, so the examples and the exit-code
# table survive --help with their line breaks intact.
_EPILOG = """\b
Examples:
  onot generate -i sbom.spdx.json
  onot generate -i sbom.cdx.json -f html -f pdf -o ./notices
  onot generate -i sbom.xlsx -f text --stdout > NOTICE.txt
  onot init                                  # a commented onot.yaml to start from
  onot generate -i sbom.spdx.json --json     # machine-readable result and warnings

\b
Exit codes:
  0  success
  1  other failure
  2  input could not be read or parsed
  3  license resolution failed
  4  invalid configuration
"""

app = typer.Typer(
    add_completion=False,
    help="onot - generate OSS notices from SBOM documents.",
    epilog=_EPILOG,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: ARG001 — consumed by the eager callback
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Print the version and exit.",
    ),
) -> None:
    """onot - generate OSS notices from SBOM documents."""


# exit codes: 2=ingest, 3=license, 4=config, 1=other (documented in _EPILOG and the README)
_EXIT_CODES = {IngestError: 2, LicenseError: 3, ConfigError: 4}


def _exit_code(err: OnotError) -> int:
    for kind, code in _EXIT_CODES.items():
        if isinstance(err, kind):
            return code
    return 1


def _build_resolver(settings, *, strict: bool) -> LicenseResolver:
    """Offline: bundled catalog only. Online: inject a remote fetcher + disk cache."""
    if settings.offline:
        return LicenseResolver(offline=True, strict=strict)
    version = SpdxLicenseCatalog.bundled().version
    return LicenseResolver(
        offline=False,
        strict=strict,
        fetcher=RemoteLicenseFetcher(),
        cache=DiskCache(f"licenses-{version}"),
    )


@app.command()
def generate(
    input: Path = typer.Option(  # noqa: A002
        ...,
        "-i",
        "--input",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to the SBOM file. The format is detected from the extension and contents.",
    ),
    formats: list[str] = typer.Option(
        ["html"],
        "-f",
        "--format",
        help="Output format: html, text (txt), markdown (md), pdf. Repeat for several.",
    ),
    output_dir: Path = typer.Option(
        Path("output"), "-o", "--output-dir", help="Directory to write the notices into."
    ),
    lang: str | None = typer.Option(
        None, "--lang", help="Output language. Only en is available at present."
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        exists=True,
        dir_okay=False,
        help=(
            "Path to onot.yaml, holding organization, contact_email, copyright_holder, "
            "copyright_year and source_download_url."
        ),
    ),
    offline: bool = typer.Option(
        True,
        "--offline/--online",
        help="Look up missing license texts remotely instead of using bundled texts only.",
    ),
    strict: bool = typer.Option(False, "--strict", help="Treat unknown licenses as errors."),
    stdout: bool = typer.Option(
        False, "--stdout", help="Write a single non-binary format to stdout instead of a file."
    ),
    quiet: bool = typer.Option(
        False, "--quiet", "-q", help="Suppress warnings. Errors still print."
    ),
    as_json: bool = typer.Option(
        False, "--json", help="Report the written files and the warnings as JSON on stdout."
    ),
) -> None:
    """Generate an OSS notice from an SBOM."""
    formats = list(dict.fromkeys(formats))  # de-duplicate (preserve order)
    unknown = [f for f in formats if not is_supported(f)]
    if unknown:
        typer.echo(
            f"error: unknown output format(s): {', '.join(unknown)}. "
            f"supported: {', '.join(available_formats())}",
            err=True,
        )
        raise typer.Exit(2)

    try:
        settings = load_settings(config, lang=lang, offline=offline)
        ingest_result = load_document(input)
        resolver = _build_resolver(settings, strict=strict)
        resolve_result = resolver.resolve(ingest_result.document)
    except OnotError as err:
        typer.echo(f"error: {err}", err=True)
        raise typer.Exit(_exit_code(err)) from err

    warnings = [*ingest_result.warnings, *resolve_result.warnings]
    # Warnings go to stderr as before. A large SBOM can emit hundreds of them, so a count by
    # kind follows, which is what tells you whether they matter. --json carries the same
    # information on stdout instead, for a caller that has to act on it.
    if not quiet and not as_json:
        for warning in warnings:
            typer.secho(f"warning: {warning}", err=True, fg="yellow")
        summary = summarize(warnings)
        if summary:
            typer.secho(summary, err=True, fg="yellow")

    doc = resolve_result.document
    now = datetime.now()

    if stdout:
        if as_json:
            typer.echo("error: --stdout and --json both write to stdout", err=True)
            raise typer.Exit(1)
        if len(formats) != 1:
            typer.echo("error: --stdout requires exactly one --format", err=True)
            raise typer.Exit(1)
        renderer = get_renderer(formats[0], settings=settings)
        if renderer.binary:
            typer.echo(f"error: {formats[0]} is binary; cannot write to stdout", err=True)
            raise typer.Exit(1)
        typer.echo(render(doc, formats[0], settings=settings, now=now), nl=False)
        return

    writer = OutputWriter()
    written: list[dict[str, str]] = []
    for fmt in formats:
        renderer = get_renderer(fmt, settings=settings)
        content = render(doc, fmt, settings=settings, now=now)
        filename = output_filename(doc.name, renderer.file_extension, now)
        path = writer.write(content, output_dir / filename)
        written.append({"format": fmt, "path": str(path)})
        if not as_json:
            typer.echo(f"wrote {path}")

    if as_json:
        typer.echo(
            json.dumps(
                {"product": doc.name, "written": written, "warnings": warnings},
                indent=2,
            )
        )


# Every key is optional and every value here is a placeholder: the point is that a reader can
# see the whole schema at once rather than going to read config.py for the field names.
_CONFIG_TEMPLATE = """\
# onot configuration. Pass it with: onot generate -i sbom.spdx.json --config onot.yaml
# Every field is optional. Anything left out falls back to the SBOM's own creation info.

company:
  # Shown as the publisher of the notice.
  organization: ""
  # Where a reader should write with open source compliance questions.
  contact_email: ""
  # Named in the copyright footer. Defaults to the organization.
  copyright_holder: ""
  # Four-digit year for that footer. Defaults to the SBOM creation year.
  copyright_year:
  # Where the corresponding source code can be obtained.
  source_download_url: ""

# Output language. en is the only one at present.
default_lang: en
# Notice theme, matching a directory under onot/rendering/themes.
theme: default
# Keep to the bundled license texts instead of fetching missing ones.
offline: true
"""


@app.command()
def init(
    path: Path = typer.Option(
        Path("onot.yaml"), "-o", "--output", help="Where to write the configuration file."
    ),
    force: bool = typer.Option(False, "--force", help="Overwrite the file if it already exists."),
) -> None:
    """Write a commented onot.yaml to start from."""
    if path.exists() and not force:
        typer.echo(f"error: {path} already exists. Pass --force to overwrite it.", err=True)
        raise typer.Exit(1)
    path.write_text(_CONFIG_TEMPLATE, encoding="utf-8")
    typer.echo(f"wrote {path}")


@app.command()
def formats() -> None:
    """Print the supported output formats."""
    for fmt in available_formats():
        typer.echo(fmt)


@app.command()
def version() -> None:
    """Print the version."""
    typer.echo(__version__)
