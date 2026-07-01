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


def _serialization(data: bytes) -> str:
    """Detect the SPDX serialization from content so parsing does not depend on the file extension.

    spdx-tools' parse_file selects its reader from the file name, so a valid document with a
    non-standard extension would fail. Returns "json"/"yaml"/"tagvalue"/"xml", or "" if unknown
    (falls back to the extension-based reader).
    """
    head = data[:8192]
    stripped = head.lstrip()
    lowered = head.lower()
    if stripped.startswith(b"<") or b"<rdf:rdf" in lowered or b"spdx.org/rdf" in lowered:
        return "xml"
    if stripped.startswith(b"{") or b'"spdxversion"' in lowered:
        return "json"
    if stripped.startswith(b"SPDXVersion:") or b"\nSPDXVersion:" in head:
        return "tagvalue"
    if b"spdxversion:" in lowered:
        return "yaml"
    return ""


def _parse_spdx(path: Path, serialization: str) -> object:
    path_str = str(path)
    if serialization == "json":
        from spdx_tools.spdx.parser.json import json_parser

        return json_parser.parse_from_file(path_str)
    if serialization == "yaml":
        from spdx_tools.spdx.parser.yaml import yaml_parser

        return yaml_parser.parse_from_file(path_str)
    if serialization == "tagvalue":
        from spdx_tools.spdx.parser.tagvalue import tagvalue_parser

        return tagvalue_parser.parse_from_file(path_str)
    # xml/rdf or unknown: fall back to the extension-based dispatcher (unchanged behavior)
    from spdx_tools.spdx.parser.parse_anything import parse_file

    return parse_file(path_str)


class SpdxAdapter:
    format_id = "spdx"

    def sniff(self, path: Path, head: bytes) -> float:
        lowered = head.lower()
        if b'"spdxversion"' in lowered:
            return 0.95
        stripped = head.lstrip()
        if stripped.startswith(b"SPDXVersion:") or b"\nSPDXVersion:" in head:
            return 0.95
        # YAML SPDX uses an unquoted lowercase key (spdxVersion:), which the JSON/tag-value
        # checks above miss. Detect it by content so a .yaml/extensionless file is recognized.
        if b"spdxversion:" in lowered:
            return 0.9
        if b"spdx.org/rdf" in lowered or (b"<rdf:rdf" in lowered and b"spdx" in lowered):
            return 0.85
        if path.name.lower().endswith((".spdx", ".spdx.json", ".spdx.yaml", ".spdx.yml")):
            return 0.7
        return 0.0

    def parse(self, path: Path) -> IngestResult:
        data = path.read_bytes()
        serialization = _serialization(data)
        if serialization == "xml" or path.name.lower().endswith(_XML_SUFFIXES):
            reject_dangerous_xml(data)
        try:
            document = _parse_spdx(path, serialization)
        except Exception as exc:  # noqa: BLE001 — wrap the library exception as a domain exception
            raise ParseError(f"failed to parse SPDX document: {path.name}") from exc
        return IngestResult(document=spdx_document_to_notice(document))
