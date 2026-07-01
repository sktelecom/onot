# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""SpdxAdapter: package mapping, NOASSERTION handling, organization/email, extracted license, errors."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from onot.domain.errors import ParseError
from onot.ingest import load_document
from onot.ingest.spdx import SpdxAdapter, _serialization

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
    # licenseDeclared=NOASSERTION -> None, concluded=Apache-2.0 -> effective
    assert bar.license_declared is None
    assert bar.effective_expression.raw == "Apache-2.0"
    # copyrightText=NOASSERTION -> structured as Copyright(is_noassertion), displays as empty string
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


def test_spdx_json_parses_with_nonstandard_extension(tmp_path):
    # O-2: serialization is detected from content, so a valid SPDX JSON parses even when
    # the file extension is non-standard (spdx-tools' parse_file would otherwise fail on it).
    weird = tmp_path / "renamed.weirdext"
    weird.write_bytes((FIX / "example.spdx.json").read_bytes())
    doc = load_document(weird).document
    assert doc.name == "example-product"


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (b'{"spdxVersion": "SPDX-2.3"}', "json"),
        (b"  \n{ }", "json"),
        (b"SPDXVersion: SPDX-2.3\nDataLicense: CC0-1.0", "tagvalue"),
        (b"spdxVersion: SPDX-2.3\n", "yaml"),
        (b'<rdf:RDF xmlns:spdx="http://spdx.org/rdf/terms#">', "xml"),
        (b"just some text", ""),
    ],
)
def test_serialization_detects_format_from_content(data, expected):
    # O-2: serialization is chosen by content so a non-standard extension does not break parsing.
    assert _serialization(data) == expected


def test_spdx_yaml_is_detected_by_content_and_parses(tmp_path):
    # O-7: SPDX YAML uses an unquoted lowercase key (spdxVersion:); it must be recognized by
    # content and parse even with a plain .yaml name (which file-name-based detection misses).
    data = yaml.safe_dump(json.loads((FIX / "example.spdx.json").read_text()))
    assert SpdxAdapter().sniff(Path("plain.yaml"), data.encode()[:8192]) > 0
    p = tmp_path / "plain.yaml"
    p.write_text(data)
    assert load_document(p).document.name == "example-product"


def test_spdx_parse_error_uses_the_given_filename(tmp_path):
    # O-1: the error references the file's own name, not an internal temp name.
    bad = tmp_path / "broken.spdx.json"
    bad.write_text("not a real sbom")
    with pytest.raises(ParseError, match="broken.spdx.json"):
        SpdxAdapter().parse(bad)
