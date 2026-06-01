"""포맷 어댑터 레지스트리 + load_document 진입점."""

from __future__ import annotations

from pathlib import Path

from onot.domain.errors import UnsupportedFormatError
from onot.ingest.base import IngestAdapter, IngestResult
from onot.ingest.cyclonedx import CycloneDxAdapter
from onot.ingest.excel import ExcelAdapter
from onot.ingest.spdx import SpdxAdapter

ADAPTERS: tuple[IngestAdapter, ...] = (SpdxAdapter(), CycloneDxAdapter(), ExcelAdapter())

_HEAD_BYTES = 8192


def best_adapter(path: Path, head: bytes | None = None) -> IngestAdapter:
    if head is None:
        head = path.read_bytes()[:_HEAD_BYTES]
    best_score = 0.0
    best: IngestAdapter | None = None
    for adapter in ADAPTERS:
        score = adapter.sniff(path, head)
        if score > best_score:
            best_score, best = score, adapter
    if best is None or best_score <= 0:
        raise UnsupportedFormatError(f"unsupported or unrecognized SBOM format: {path.name}")
    return best


def load_document(path: str | Path) -> IngestResult:
    target = Path(path)
    return best_adapter(target).parse(target)


def available_formats() -> tuple[str, ...]:
    return tuple(adapter.format_id for adapter in ADAPTERS)
