# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""포맷 자동 감지(확장자 힌트 + 내용 스니핑)."""

from __future__ import annotations

from pathlib import Path

from onot.ingest.registry import best_adapter


def detect_format(path: str | Path) -> str:
    """가장 신뢰도 높은 어댑터의 format_id를 반환(없으면 UnsupportedFormatError)."""
    target = Path(path)
    return best_adapter(target).format_id
