"""CycloneDxAdapter — cyclonedx-python-lib로 CycloneDX(JSON/XML) 파싱.

CDX는 concluded/declared 구분이 없어 라이선스를 license_declared로 매핑한다(effective가
declared로 폴백). 인라인 named 라이선스는 즉석 LicenseRef로 등록. XML은 defusedxml로
XXE 안전 파싱한다.
"""

from __future__ import annotations

import json
from pathlib import Path

from onot.core.naming import slugify
from onot.domain.errors import IngestValidationError, ParseError
from onot.domain.models import Copyright, LicenseExpression, LicenseRef, NoticeDocument, Package
from onot.ingest._xml_guard import reject_dangerous_xml
from onot.ingest.base import IngestResult


class CycloneDxAdapter:
    format_id = "cyclonedx"

    def sniff(self, path: Path, head: bytes) -> float:
        lowered = head.lower()
        if b'"bomformat"' in lowered and b"cyclonedx" in lowered:
            return 0.97
        if b"<bom" in lowered and b"cyclonedx" in lowered:
            return 0.92
        return 0.0

    def parse(self, path: Path) -> IngestResult:
        data = path.read_bytes()
        is_xml = path.name.lower().endswith(".xml") or data.lstrip().startswith(b"<")
        try:
            bom = self._parse_xml(data) if is_xml else self._parse_json(data)
        except (ParseError, IngestValidationError):
            raise  # XXE 거부·파싱 오류는 그대로 전파
        except Exception as exc:  # noqa: BLE001
            raise ParseError(f"failed to parse CycloneDX document: {path.name}") from exc
        return IngestResult(document=_bom_to_notice(bom))

    @staticmethod
    def _parse_json(data: bytes):
        from cyclonedx.model.bom import Bom

        return Bom.from_json(json.loads(data))

    @staticmethod
    def _parse_xml(data: bytes):
        from cyclonedx.model.bom import Bom
        from defusedxml.common import DefusedXmlException
        from defusedxml.ElementTree import fromstring

        reject_dangerous_xml(data)
        try:
            element = fromstring(data)
        except DefusedXmlException as exc:  # 인코딩 우회 등 2차 방어
            raise IngestValidationError(["unsafe XML rejected (XXE protection)"]) from exc
        return Bom.from_xml(element)


def _register_named_ref(name: str, text: str, refs: dict[str, LicenseRef]) -> str:
    """named 라이선스를 LicenseRef로 등록하고 id 반환. slug 충돌은 suffix로 분리(무음 덮어쓰기 방지)."""
    base = f"LicenseRef-{slugify(name)}"
    candidate = base
    suffix = 2
    # 같은 name+text면 재사용(dedup), 다르면(slug 충돌) suffix로 분리
    while candidate in refs and (
        refs[candidate].name != name or refs[candidate].extracted_text != text
    ):
        candidate = f"{base}-{suffix}"
        suffix += 1
    refs[candidate] = LicenseRef(identifier=candidate, name=name, extracted_text=text)
    return candidate


def _license_parts(component: object, refs: dict[str, LicenseRef]) -> list[str]:
    parts: list[str] = []
    for lic in getattr(component, "licenses", None) or []:
        value = getattr(lic, "value", None)  # CDX LicenseExpression
        if value:
            parts.append(value)
            continue
        license_id = getattr(lic, "id", None)
        if license_id:
            parts.append(license_id)
            continue
        name = getattr(lic, "name", None)
        if name:
            text_obj = getattr(lic, "text", None)
            text = getattr(text_obj, "content", "") or "" if text_obj is not None else ""
            parts.append(_register_named_ref(name, text, refs))
    return parts


def _bom_to_notice(bom: object) -> NoticeDocument:
    refs: dict[str, LicenseRef] = {}
    packages: list[Package] = []
    for component in getattr(bom, "components", None) or []:
        parts = _license_parts(component, refs)
        expression = " AND ".join(parts) if parts else None
        version = getattr(component, "version", None)
        purl = getattr(component, "purl", None)
        packages.append(
            Package(
                name=component.name,
                version=str(version) if version else "",
                license_declared=LicenseExpression.from_raw(expression),
                copyright=Copyright.from_raw(getattr(component, "copyright", None)),
                purl=str(purl) if purl else None,
            )
        )
    metadata = getattr(bom, "metadata", None)
    main_component = getattr(metadata, "component", None) if metadata else None
    name = (getattr(main_component, "name", None) if main_component else None) or "OSS Notice"
    return NoticeDocument(name=name, packages=tuple(packages), license_refs=tuple(refs.values()))
