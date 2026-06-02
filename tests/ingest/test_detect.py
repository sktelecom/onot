"""포맷 자동 감지: 확장자+내용 스니핑, .json 모호성 해소, 미지원 거부."""

from __future__ import annotations

from pathlib import Path

import pytest

from onot.domain.errors import UnsupportedFormatError
from onot.ingest import detect_format

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "sbom"
ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    ("name", "fmt"),
    [
        ("example.spdx.json", "spdx"),
        ("example.cdx.json", "cyclonedx"),
        ("example.cdx.xml", "cyclonedx"),
    ],
)
def test_detect_fixtures(name, fmt):
    assert detect_format(FIX / name) == fmt


def test_detect_excel():
    assert detect_format(ROOT / "tests" / "fixtures" / "sbom" / "example.spdx.xlsx") == "excel"


def test_json_disambiguation(tmp_path):
    # SPDX JSON과 CycloneDX JSON이 둘 다 .json — 내용으로 구분
    spdx = tmp_path / "a.json"
    spdx.write_text('{"spdxVersion":"SPDX-2.3","name":"x"}')
    cdx = tmp_path / "b.json"
    cdx.write_text('{"bomFormat":"CycloneDX","specVersion":"1.5"}')
    assert detect_format(spdx) == "spdx"
    assert detect_format(cdx) == "cyclonedx"


def test_unsupported_format(tmp_path):
    path = tmp_path / "x.txt"
    path.write_text("just some text, not an sbom")
    with pytest.raises(UnsupportedFormatError):
        detect_format(path)
