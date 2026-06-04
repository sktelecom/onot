# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Automatic format detection (extension hint + content sniffing)."""

from __future__ import annotations

from pathlib import Path

from onot.ingest.registry import best_adapter


def detect_format(path: str | Path) -> str:
    """Return the format_id of the highest-confidence adapter (raises UnsupportedFormatError if none)."""
    target = Path(path)
    return best_adapter(target).format_id
