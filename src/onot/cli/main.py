"""onot CLI 진입점 (Typer).

M0.5 슬라이스: `onot generate -i <xlsx> -o <html>` 와 `onot version`.
M5에서 다중 포맷(-f), --output-dir, --lang, --config, formats 커맨드로 확장된다.
"""

from __future__ import annotations

from pathlib import Path

import typer

from onot import __version__
from onot.ingest.excel import parse_excel
from onot.license import resolve
from onot.rendering.html import render_html

app = typer.Typer(add_completion=False, help="onot — OSS notice generator")


@app.command()
def generate(
    input: Path = typer.Option(  # noqa: A002 — CLI 관용
        ..., "-i", "--input", exists=True, dir_okay=False, readable=True, help="입력 SBOM(Excel)"
    ),
    output: Path = typer.Option(..., "-o", "--output", help="출력 HTML 경로"),
) -> None:
    """SBOM에서 OSS 고지문(HTML)을 생성한다."""
    doc = parse_excel(input)
    doc = resolve(doc)
    html = render_html(doc)
    output.write_text(html, encoding="utf-8")
    typer.echo(f"wrote {output}")


@app.command()
def version() -> None:
    """버전을 출력한다."""
    typer.echo(__version__)
