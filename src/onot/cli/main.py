# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""onot CLI entry point (Typer).

generate (multiple formats, auto-detection, language, settings), formats, version.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer

from onot import __version__
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

app = typer.Typer(add_completion=False, help="onot — OSS notice generator")

# exit codes: 2=ingest, 3=license, 4=config, 1=other
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
        ..., "-i", "--input", exists=True, dir_okay=False, readable=True, help="input SBOM"
    ),
    formats: list[str] = typer.Option(
        ["html"], "-f", "--format", help="output format (repeatable)"
    ),
    output_dir: Path = typer.Option(Path("output"), "-o", "--output-dir", help="output directory"),
    lang: str | None = typer.Option(None, "--lang", help="output language (en)"),
    config: Path | None = typer.Option(
        None, "--config", exists=True, dir_okay=False, help="onot.yaml config"
    ),
    offline: bool = typer.Option(
        True, "--offline/--online", help="disable remote license fetching"
    ),
    strict: bool = typer.Option(False, "--strict", help="treat unknown licenses as errors"),
    stdout: bool = typer.Option(False, "--stdout", help="write a single text format to stdout"),
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

    for warning in (*ingest_result.warnings, *resolve_result.warnings):
        typer.echo(f"warning: {warning}", err=True)

    doc = resolve_result.document
    now = datetime.now()

    if stdout:
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
    for fmt in formats:
        renderer = get_renderer(fmt, settings=settings)
        content = render(doc, fmt, settings=settings, now=now)
        filename = output_filename(doc.name, renderer.file_extension, now)
        path = writer.write(content, output_dir / filename)
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
