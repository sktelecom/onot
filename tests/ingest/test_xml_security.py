"""XML 입력 보안(R-ING-2): XXE·확장 폭탄 거부."""

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
    # 정상 XML은 통과(예외 없음)
    reject_dangerous_xml(b'<?xml version="1.0"?><bom><components/></bom>')


def test_guard_rejects_doctype_and_entity():
    with pytest.raises(IngestValidationError):
        reject_dangerous_xml(b"<!DOCTYPE x><x/>")
    with pytest.raises(IngestValidationError):
        reject_dangerous_xml(b'<!ENTITY y "z"><x/>')


@pytest.mark.parametrize("encoding", ["utf-16", "utf-16-le", "utf-16-be", "utf-32"])
def test_encoding_bypass_blocked(encoding):
    # ASCII regex를 우회하려 인코딩한 DTD/ENTITY도 차단(L3 #1 회귀)
    payload = '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY e "v">]><bom/>'.encode(encoding)
    with pytest.raises(IngestValidationError):
        reject_dangerous_xml(payload)


def test_spdx_rdf_xxe_rejected(tmp_path):
    # SPDX RDF 경로(2차 방어 없음)도 가드로 거부(L3 #2 회귀)
    from onot.ingest.spdx import SpdxAdapter

    bad = tmp_path / "x.rdf"
    bad.write_bytes(
        b'<?xml version="1.0"?><!DOCTYPE r [<!ENTITY e SYSTEM "file:///etc/passwd">]>'
        b'<rdf:RDF xmlns:spdx="http://spdx.org/rdf/terms#"/>'
    )
    with pytest.raises(IngestValidationError):
        SpdxAdapter().parse(bad)
