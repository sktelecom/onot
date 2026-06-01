"""렌더러 4종: 포맷별 산출, 메타데이터, 미지원 포맷, PDF(있으면)."""

from __future__ import annotations

from pathlib import Path

import pytest

from onot.ingest.excel import parse_excel
from onot.license import resolve
from onot.rendering import available_formats, get_renderer, render

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "sample" / "SPDXRdfExample-v2.3.xlsx"


@pytest.fixture(scope="module")
def doc():
    return resolve(parse_excel(SAMPLE))


@pytest.mark.parametrize("fmt", ["html", "text", "markdown"])
def test_text_formats_render(doc, fmt):
    out = render(doc, fmt)
    assert isinstance(out, str)
    assert "SPDX-Tools-v2.0" in out


def test_available_formats():
    assert available_formats() == ("html", "text", "markdown", "pdf")


def test_unknown_format_raises(doc):
    with pytest.raises(ValueError, match="unknown output format"):
        render(doc, "xml")


def test_renderer_metadata():
    assert get_renderer("html").file_extension == "html"
    assert get_renderer("text").file_extension == "txt"
    assert get_renderer("md").format_id == "markdown"
    assert get_renderer("pdf").binary is True


def test_pdf_renders_when_available(doc):
    pytest.importorskip("weasyprint")
    out = render(doc, "pdf")
    assert isinstance(out, bytes)
    assert out[:5] == b"%PDF-"


def test_pdf_missing_weasyprint_raises(doc, monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "weasyprint", None)  # from weasyprint import → ImportError
    with pytest.raises(RuntimeError, match=r"onot\[pdf\]"):
        render(doc, "pdf")


def test_full_render_all_langs_exercises_all_i18n_keys():
    # source_url/closing/footer 등 플레이스홀더 키를 양 언어·전 포맷에서 KeyError 없이 렌더
    from datetime import datetime

    from onot.core.config import CompanyConfig, Settings
    from onot.domain.models import (
        License,
        LicenseExpression,
        NoticeDocument,
        Package,
        PackageRef,
    )

    settings = Settings(
        company=CompanyConfig(
            organization="SKT",
            contact_email="oss@skt.example",
            copyright_holder="SK telecom",
            copyright_year=2024,
            source_download_url="https://example.com/src",
        )
    )
    doc = NoticeDocument(
        name="Product",
        packages=(Package(name="p", license_declared=LicenseExpression(raw="MIT")),),
        licenses=(
            License(license_id="MIT", name="MIT", text="t", used_by=(PackageRef(name="p"),)),
        ),
    )
    for lang in ("en", "ko"):
        for fmt in ("html", "text", "markdown"):
            out = render(doc, fmt, settings=settings, lang=lang, now=datetime(2024, 1, 1))
            assert "https://example.com/src" in out
            assert "oss@skt.example" in out
            assert "SK telecom" in out
