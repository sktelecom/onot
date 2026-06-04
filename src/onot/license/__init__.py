# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""License resolution layer.

The default `resolve()` does offline resolution based on the bundled catalog (air-gapped,
deterministic). Inject a fetcher into LicenseResolver if online supplementation is needed.
"""

from __future__ import annotations

from onot.domain.models import NoticeDocument
from onot.license.resolver import LicenseResolver, ResolveResult

__all__ = ["LicenseResolver", "ResolveResult", "resolve", "resolve_with_warnings"]


def resolve_with_warnings(doc: NoticeDocument) -> ResolveResult:
    """Offline resolution result based on the bundled catalog (includes warnings)."""
    return LicenseResolver().resolve(doc)


def resolve(doc: NoticeDocument) -> NoticeDocument:
    """Return a NoticeDocument with full texts filled in (warnings discarded)."""
    return resolve_with_warnings(doc).document
