# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Defense against XXE and expansion bombs (billion-laughs) in untrusted XML input.

Rather than relying on the library's internal parser, this rejects DOCTYPE/ENTITY
declarations before parsing. SBOM XML (CycloneDX/SPDX-RDF) needs no DTD, so any occurrence
is blocked immediately.

To prevent attempts to bypass the ASCII regex by encoding as UTF-16/UTF-32 etc., it inspects
not only the original bytes but also a null-byte-stripped copy and copies decoded under
several encodings.
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
    """Reject with IngestValidationError if a DTD/external entity is found (including encoding bypasses)."""
    for blob in _candidates(data):
        if _DOCTYPE.search(blob) or _ENTITY.search(blob):
            raise IngestValidationError(
                ["XML DTD/ENTITY declarations are not allowed (XXE protection)"]
            )
