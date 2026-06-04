# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""CycloneDxAdapter: JSON/XML, id/expression/named licenses, purl, copyright, errors."""

from __future__ import annotations

from pathlib import Path

import pytest

from onot.domain.errors import ParseError
from onot.ingest import load_document
from onot.ingest.cyclonedx import CycloneDxAdapter

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "sbom"


def test_cdx_json_id_and_named_license():
    doc = load_document(FIX / "example.cdx.json").document
    assert doc.name == "example-product"
    packages = {p.name: p for p in doc.packages}

    foo = packages["foo"]
    assert foo.effective_expression.raw == "MIT"
    assert foo.purl == "pkg:pypi/foo@1.2.3"
    assert foo.copyright.text == "Copyright 2024 Foo Authors"

    # Named license (no id) -> registered as LicenseRef + the expression is that id
    bar = packages["bar"]
    assert bar.effective_expression.raw == "LicenseRef-Custom_Bar_License"
    refs = {r.identifier: r for r in doc.license_refs}
    assert refs["LicenseRef-Custom_Bar_License"].name == "Custom Bar License"
    assert "anything with Bar" in refs["LicenseRef-Custom_Bar_License"].extracted_text


def test_cdx_xml_expression():
    doc = load_document(FIX / "example.cdx.xml").document
    packages = {p.name: p for p in doc.packages}
    assert packages["foo"].effective_expression.raw == "MIT"
    assert packages["baz"].effective_expression.raw == "Apache-2.0 OR MIT"


def test_cdx_malformed_raises_parse_error(tmp_path):
    bad = tmp_path / "bad.cdx.json"
    bad.write_text('{"bomFormat":"CycloneDX","components":[{"name": }]}')
    with pytest.raises(ParseError):
        CycloneDxAdapter().parse(bad)


def test_named_license_slug_collision_disambiguated():
    # Distinct names colliding on the same slug are kept separate, no silent overwrite (L3 blocking regression)
    from onot.ingest.cyclonedx import _register_named_ref

    refs: dict = {}
    a = _register_named_ref("Foo & Bar", "TEXT A", refs)
    b = _register_named_ref("Foo + Bar", "TEXT B", refs)  # same slug "Foo_Bar"
    assert a != b
    assert refs[a].extracted_text == "TEXT A"
    assert refs[b].extracted_text == "TEXT B"
    # Same name+text reuses the same id (dedup)
    assert _register_named_ref("Foo & Bar", "TEXT A", refs) == a
