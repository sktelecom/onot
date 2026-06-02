"""라이선스 전문 디스크 캐시(platformdirs). 네임스페이스에 라이선스 리스트 버전 포함."""

from __future__ import annotations

import hashlib
from pathlib import Path

import platformdirs


class DiskCache:
    def __init__(self, namespace: str, *, base_dir: Path | None = None) -> None:
        root = base_dir or Path(platformdirs.user_cache_dir("onot"))
        self.dir = root / namespace

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]
        return self.dir / f"{digest}.txt"

    def get(self, key: str) -> str | None:
        try:
            return self._path(key).read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            return None

    def set(self, key: str, value: str) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        self._path(key).write_text(value, encoding="utf-8")
