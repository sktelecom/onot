# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""입력 어댑터: 외부 포맷 → onot.domain.NoticeDocument."""

from onot.ingest.base import IngestAdapter, IngestResult
from onot.ingest.detect import detect_format
from onot.ingest.registry import available_formats, load_document

__all__ = [
    "IngestAdapter",
    "IngestResult",
    "available_formats",
    "detect_format",
    "load_document",
]
