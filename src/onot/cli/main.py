# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""onot CLI 진입점 (Typer).

generate(다중 포맷·자동감지·언어·설정), formats, version.
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

# 종료 코드: 2=입력, 3=라이선스, 4=설정, 1=기타
_EXIT_CODES = {IngestError: 2, LicenseError: 3, ConfigError: 4}


def _exit_code(err: OnotError) -> int:
    for kind, code in _EXIT_CODES.items():
        if isinstance(err, kind):
            return code
    return 1


def _build_resolver(settings, *, strict: bool) -> LicenseResolver:
    """오프라인이면 번들만, 온라인이면 원격 fetcher + 디스크 캐시를 주입."""
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
        ..., "-i", "--input", exists=True, dir_okay=False, readable=True, help="입력 SBOM"
    ),
    formats: list[str] = typer.Option(["html"], "-f", "--format", help="출력 포맷(반복 가능)"),
    output_dir: Path = typer.Option(Path("output"), "-o", "--output-dir", help="출력 디렉터리"),
    lang: str | None = typer.Option(None, "--lang", help="ko 또는 en"),
    config: Path | None = typer.Option(
        None, "--config", exists=True, dir_okay=False, help="onot.yaml 설정"
    ),
    offline: bool = typer.Option(True, "--offline/--online", help="라이선스 원격 보충 비활성"),
    strict: bool = typer.Option(False, "--strict", help="unknown 라이선스를 오류로"),
    stdout: bool = typer.Option(False, "--stdout", help="단일 텍스트 포맷을 표준출력으로"),
) -> None:
    """SBOM에서 OSS 고지문을 생성한다."""
    formats = list(dict.fromkeys(formats))  # 중복 제거(순서 보존)
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
    """지원하는 출력 포맷을 출력한다."""
    for fmt in available_formats():
        typer.echo(fmt)


@app.command()
def version() -> None:
    """버전을 출력한다."""
    typer.echo(__version__)
