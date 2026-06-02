"""신뢰할 수 없는 XML 입력의 XXE·확장 폭탄(billion-laughs) 방어.

라이브러리 내부 파서에 의존하지 않고, 파싱 전에 DOCTYPE/ENTITY 선언을 거부한다.
SBOM XML(CycloneDX/SPDX-RDF)에는 DTD가 필요 없으므로 발견 즉시 차단한다.

UTF-16/UTF-32 등으로 인코딩해 ASCII regex를 우회하는 시도를 막기 위해, 원본 바이트뿐
아니라 null 바이트 제거본과 여러 인코딩 디코딩본을 함께 검사한다.
"""

from __future__ import annotations

import re

from onot.domain.errors import IngestValidationError

_DOCTYPE = re.compile(rb"<!DOCTYPE", re.IGNORECASE)
_ENTITY = re.compile(rb"<!ENTITY", re.IGNORECASE)
_ENCODINGS = ("utf-8", "utf-16", "utf-16-le", "utf-16-be", "utf-32")


def _candidates(data: bytes) -> list[bytes]:
    blobs = [data, data.replace(b"\x00", b"")]
    for encoding in _ENCODINGS:
        try:
            blobs.append(data.decode(encoding).encode("utf-8"))
        except (UnicodeDecodeError, LookupError, ValueError):
            continue
    return blobs


def reject_dangerous_xml(data: bytes) -> None:
    """DTD/외부 엔티티가 보이면(인코딩 우회 포함) IngestValidationError로 거부."""
    for blob in _candidates(data):
        if _DOCTYPE.search(blob) or _ENTITY.search(blob):
            raise IngestValidationError(
                ["XML DTD/ENTITY declarations are not allowed (XXE protection)"]
            )
