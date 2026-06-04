# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""SpdxAdapter — parses SPDX 2.x (JSON/YAML/Tag-Value/RDF) via spdx-tools.

SPDX 3.0 input is deferred (D-005). For RDF/XML, an XXE guard is applied before parsing.
"""

from __future__ import annotations

from pathlib import Path

from onot.domain.errors import ParseError
from onot.ingest._mapping import spdx_document_to_notice
from onot.ingest._xml_guard import reject_dangerous_xml
from onot.ingest.base import IngestResult

_XML_SUFFIXES = (".rdf", ".rdf.xml", ".xml")


class SpdxAdapter:
    format_id = "spdx"

    def sniff(self, path: Path, head: bytes) -> float:
        lowered = head.lower()
        if b'"spdxversion"' in lowered:
            return 0.95
        stripped = head.lstrip()
        if stripped.startswith(b"SPDXVersion:") or b"\nSPDXVersion:" in head:
            return 0.95
        if b"spdx.org/rdf" in lowered or (b"<rdf:rdf" in lowered and b"spdx" in lowered):
            return 0.85
        if path.name.lower().endswith((".spdx", ".spdx.json", ".spdx.yaml", ".spdx.yml")):
            return 0.7
        return 0.0

    def parse(self, path: Path) -> IngestResult:
        if path.name.lower().endswith(_XML_SUFFIXES):
            reject_dangerous_xml(path.read_bytes())
        from spdx_tools.spdx.parser.parse_anything import parse_file

        try:
            document = parse_file(str(path))
        except Exception as exc:  # noqa: BLE001 — wrap the library exception as a domain exception
            raise ParseError(f"failed to parse SPDX document: {path.name}") from exc
        return IngestResult(document=spdx_document_to_notice(document))
