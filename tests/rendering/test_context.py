"""컨텍스트 병합: 회사 설정 우선, SBOM 폴백, 연도 추론, 생성일 주입."""

from __future__ import annotations

from datetime import datetime

from onot.core.config import CompanyConfig, Settings
from onot.domain.models import CreationInfo, NoticeDocument
from onot.rendering.context import build_context


def _doc(**ci):
    return NoticeDocument(name="prod", creation_info=CreationInfo(**ci))


def test_company_overrides_sbom():
    settings = Settings(company=CompanyConfig(organization="SKT", contact_email="c@skt.example"))
    ctx = build_context(_doc(organization="FromSBOM", email="s@sbom.example"), settings)
    assert ctx.organization == "SKT"
    assert ctx.email == "c@skt.example"


def test_sbom_used_when_company_blank():
    ctx = build_context(_doc(organization="FromSBOM", email="s@sbom.example"), Settings())
    assert ctx.organization == "FromSBOM"
    assert ctx.email == "s@sbom.example"


def test_year_from_created_when_company_blank():
    ctx = build_context(_doc(created=datetime(2021, 5, 1)), Settings())
    assert ctx.copyright_year == 2021


def test_company_year_wins():
    settings = Settings(company=CompanyConfig(copyright_year=2030))
    ctx = build_context(_doc(created=datetime(2021, 5, 1)), settings)
    assert ctx.copyright_year == 2030


def test_generated_date_injected():
    ctx = build_context(_doc(), Settings(), now=datetime(2024, 1, 2))
    assert ctx.generated == "2024-01-02"
    assert build_context(_doc(), Settings()).generated == ""
