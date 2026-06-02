"""디스크 캐시(R-LIC-3): hit/miss, 손상 내성."""

from __future__ import annotations

from onot.license.cache import DiskCache


def test_set_get_roundtrip(tmp_path):
    cache = DiskCache("licenses-3.28.0", base_dir=tmp_path)
    assert cache.get("MIT") is None
    cache.set("MIT", "the text")
    assert cache.get("MIT") == "the text"


def test_namespaces_isolated(tmp_path):
    a = DiskCache("v1", base_dir=tmp_path)
    b = DiskCache("v2", base_dir=tmp_path)
    a.set("MIT", "old")
    assert b.get("MIT") is None  # 버전 네임스페이스로 격리(자연 무효화)


def test_missing_dir_returns_none(tmp_path):
    cache = DiskCache("nope", base_dir=tmp_path / "absent")
    assert cache.get("anything") is None
