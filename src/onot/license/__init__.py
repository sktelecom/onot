# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""라이선스 해석 레이어.

기본 `resolve()`는 번들 카탈로그 기반 오프라인 해석(에어갭, 결정적)이다. 온라인 보충이
필요하면 LicenseResolver에 fetcher를 주입한다.
"""

from __future__ import annotations

from onot.domain.models import NoticeDocument
from onot.license.resolver import LicenseResolver, ResolveResult

__all__ = ["LicenseResolver", "ResolveResult", "resolve", "resolve_with_warnings"]


def resolve_with_warnings(doc: NoticeDocument) -> ResolveResult:
    """번들 카탈로그 기반 오프라인 해석 결과(경고 포함)."""
    return LicenseResolver().resolve(doc)


def resolve(doc: NoticeDocument) -> NoticeDocument:
    """전문이 채워진 NoticeDocument를 반환(경고는 버림)."""
    return resolve_with_warnings(doc).document
