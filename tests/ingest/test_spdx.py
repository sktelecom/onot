# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""SpdxAdapter: 패키지 매핑, NOASSERTION 처리, organization/email, extracted license, 오류."""

from __future__ import annotations

from pathlib import Path

import pytest

from onot.domain.errors import ParseError
from onot.ingest import load_document
from onot.ingest.spdx import SpdxAdapter

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "sbom"


def test_spdx_json_maps_document_and_packages():
    doc = load_document(FIX / "example.spdx.json").document
    assert doc.name == "example-product"
    assert doc.creation_info.organization == "Example Inc."
    assert doc.creation_info.email == "compliance@example.com"

    packages = {p.name: p for p in doc.packages}
    foo = packages["foo"]
    assert foo.effective_expression.raw == "MIT"
    assert foo.purl == "pkg:pypi/foo@1.2.3"
    assert foo.copyright.text == "Copyright 2024 Foo Authors"
    assert foo.download_location == "https://example.com/foo-1.2.3.tar.gz"


def test_spdx_noassertion_normalized_to_none():
    doc = load_document(FIX / "example.spdx.json").document
    bar = next(p for p in doc.packages if p.name == "bar")
    # licenseDeclared=NOASSERTION → None, concluded=Apache-2.0 → effective
    assert bar.license_declared is None
    assert bar.effective_expression.raw == "Apache-2.0"
    # copyrightText=NOASSERTION → Copyright(is_noassertion)로 구조화, 표시는 빈 문자열
    assert bar.copyright.is_noassertion is True
    assert bar.copyright_display == ""
    assert bar.download_location == ""  # NOASSERTION


def test_spdx_extracted_license_ref():
    doc = load_document(FIX / "example.spdx.json").document
    refs = {r.identifier: r for r in doc.license_refs}
    assert "LicenseRef-Custom" in refs
    assert refs["LicenseRef-Custom"].name == "Custom Bar License"
    assert "anything with Bar" in refs["LicenseRef-Custom"].extracted_text


def test_spdx_malformed_raises_parse_error(tmp_path):
    bad = tmp_path / "bad.spdx.json"
    bad.write_text('{"spdxVersion": "SPDX-2.3", "packages": [ this is not json ]}')
    with pytest.raises(ParseError):
        SpdxAdapter().parse(bad)
