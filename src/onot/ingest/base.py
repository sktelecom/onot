# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Common interface for input adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

from onot.domain.models import NoticeDocument


class IngestResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    document: NoticeDocument
    warnings: tuple[str, ...] = ()


@runtime_checkable
class IngestAdapter(Protocol):
    format_id: str

    def sniff(self, path: Path, head: bytes) -> float:
        """Confidence (0.0-1.0) that this adapter can handle the input."""
        ...

    def parse(self, path: Path) -> IngestResult:
        """Normalize the input into a NoticeDocument."""
        ...
