"""M0.5 수직 슬라이스 end-to-end 테스트: Excel → domain → license → HTML → CLI."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from typer.testing import CliRunner

from onot.cli.main import app
from onot.core.naming import output_filename, slugify
from onot.ingest.excel import parse_excel
from onot.license import resolve
from onot.rendering.html import render_html

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "sample" / "SPDXRdfExample-v2.3.xlsx"
GOLDEN = ROOT / "tests" / "golden" / "slice_notice.html"


def _document():
    return resolve(parse_excel(SAMPLE))


def test_parse_counts():
    doc = _document()
    assert doc.name == "SPDX-Tools-v2.0"
    assert len(doc.packages) == 4
    assert len(doc.licenses) == 10


def test_render_matches_golden():
    assert render_html(_document()) == GOLDEN.read_text(encoding="utf-8")


def test_pipeline_deterministic():
    # 재파싱→재해석→재렌더가 바이트 동일(resolver dict/정렬 결정성까지 고정)
    assert render_html(_document()) == render_html(_document())


def test_effective_expression_fallback():
    doc = parse_excel(SAMPLE)
    # concluded가 있으면 concluded, 없으면 declared
    for pkg in doc.packages:
        assert pkg.effective_expression == (pkg.license_concluded or pkg.license_declared)


def test_cli_generate(tmp_path):
    result = CliRunner().invoke(
        app, ["generate", "-i", str(SAMPLE), "-f", "html", "--output-dir", str(tmp_path)]
    )
    assert result.exit_code == 0, result.output
    files = list(tmp_path.glob("*.html"))
    assert len(files) == 1
    assert "OSS Notice for SPDX-Tools-v2.0" in files[0].read_text(encoding="utf-8")


def test_cli_version():
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip().startswith("2.")


def test_output_filename():
    now = datetime(2024, 1, 2, 3, 4, 5)
    assert (
        output_filename("My Product!", "html", now) == "OSS_Notice_My_Product_20240102_030405.html"
    )
    assert slugify("   ") == "OSS_Notice"


def test_effective_expression_independent():
    from onot.domain.models import LicenseExpression, Package

    mit = LicenseExpression(raw="MIT")
    apache = LicenseExpression(raw="Apache-2.0")
    assert (
        Package(name="x", license_concluded=mit, license_declared=apache).effective_expression
        == mit
    )
    assert Package(name="x", license_declared=apache).effective_expression == apache
    assert Package(name="x").effective_expression is None
