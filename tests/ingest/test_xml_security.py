# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""XML input security (R-ING-2): rejects XXE and expansion bombs."""

from __future__ import annotations

from pathlib import Path

import pytest

from onot.domain.errors import IngestValidationError
from onot.ingest import load_document
from onot.ingest._xml_guard import reject_dangerous_xml

FIX = Path(__file__).resolve().parents[1] / "fixtures" / "sbom"


@pytest.mark.parametrize("name", ["xxe.cdx.xml", "billion-laughs.cdx.xml"])
def test_malicious_xml_rejected(name):
    with pytest.raises(IngestValidationError):
        load_document(FIX / name)


def test_guard_allows_clean_xml():
    # Clean XML passes (no exception)
    reject_dangerous_xml(b'<?xml version="1.0"?><bom><components/></bom>')


def test_guard_rejects_doctype_and_entity():
    with pytest.raises(IngestValidationError):
        reject_dangerous_xml(b"<!DOCTYPE x><x/>")
    with pytest.raises(IngestValidationError):
        reject_dangerous_xml(b'<!ENTITY y "z"><x/>')


@pytest.mark.parametrize("encoding", ["utf-16", "utf-16-le", "utf-16-be", "utf-32"])
def test_encoding_bypass_blocked(encoding):
    # DTD/ENTITY encoded to bypass the ASCII regex is also blocked (L3 #1 regression)
    payload = '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e "v">]><bom/>'.encode(encoding)
    with pytest.raises(IngestValidationError):
        reject_dangerous_xml(payload)


def test_spdx_rdf_xxe_rejected(tmp_path):
    # The SPDX RDF path (no secondary defense) is also rejected by the guard (L3 #2 regression)
    from onot.ingest.spdx import SpdxAdapter

    bad = tmp_path / "x.rdf"
    bad.write_bytes(
        b'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY e SYSTEM "file:///etc/passwd">]>'
        b'<rdf:RDF xmlns:spdx="http://spdx.org/rdf/terms#"/>'
    )
    with pytest.raises(IngestValidationError):
        SpdxAdapter().parse(bad)
