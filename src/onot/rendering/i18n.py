"""메시지 카탈로그 기반 다국어. 누락 키는 키 자체를 반환(테스트로 정합성 검증)."""

from __future__ import annotations

from collections.abc import Mapping
from functools import cache
from importlib.resources import files
from types import MappingProxyType

import yaml

AVAILABLE_LANGS = ("en", "ko")


@cache
def _catalog(lang: str) -> Mapping[str, str]:
    resource = files("onot.rendering") / "i18n" / f"{lang}.yaml"
    data = yaml.safe_load(resource.read_text(encoding="utf-8")) or {}
    return MappingProxyType(data)  # 캐시된 카탈로그의 외부 변형 방지


class Translator:
    def __init__(self, lang: str) -> None:
        if lang not in AVAILABLE_LANGS:
            lang = "en"
        self.lang = lang
        self._catalog = _catalog(lang)

    def __call__(self, key: str, /, **kwargs: object) -> str:
        text = self._catalog.get(key, key)
        if not kwargs:
            return text
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text  # 플레이스홀더 불일치 시 렌더 중단 대신 원문 유지

    def keys(self) -> set[str]:
        return set(self._catalog)
