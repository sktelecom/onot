"""입력 어댑터 공통 인터페이스."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

from onot.domain.models import NoticeDocument


class IngestResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    document: NoticeDocument
    warnings: tuple[str, ...] = ()


@runtime_checkable
class IngestAdapter(Protocol):
    format_id: ClassVar[str]

    def sniff(self, path: Path, head: bytes) -> float:
        """이 어댑터가 입력을 처리할 신뢰도(0.0~1.0)."""
        ...

    def parse(self, path: Path) -> IngestResult:
        """입력을 NoticeDocument로 정규화."""
        ...
