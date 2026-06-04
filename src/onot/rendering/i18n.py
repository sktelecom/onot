# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Message-catalog-based i18n. A missing key returns the key itself (consistency is checked by tests)."""

from __future__ import annotations

from collections.abc import Mapping
from functools import cache
from importlib.resources import files
from types import MappingProxyType

import yaml

AVAILABLE_LANGS = ("en",)


@cache
def _catalog(lang: str) -> Mapping[str, str]:
    resource = files("onot.rendering") / "i18n" / f"{lang}.yaml"
    data = yaml.safe_load(resource.read_text(encoding="utf-8")) or {}
    return MappingProxyType(data)  # prevent external mutation of the cached catalog


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
            return text  # on placeholder mismatch, keep the original text instead of failing the render

    def keys(self) -> set[str]:
        return set(self._catalog)
