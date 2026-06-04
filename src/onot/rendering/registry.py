# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Output format -> Renderer mapping."""

from __future__ import annotations

from onot.core.config import Settings
from onot.rendering.base import Renderer
from onot.rendering.html import HtmlRenderer
from onot.rendering.markdown import MarkdownRenderer
from onot.rendering.pdf import PdfRenderer
from onot.rendering.text import TextRenderer

_RENDERERS: dict[str, type[Renderer]] = {
    "html": HtmlRenderer,
    "text": TextRenderer,
    "txt": TextRenderer,
    "markdown": MarkdownRenderer,
    "md": MarkdownRenderer,
    "pdf": PdfRenderer,
}


def get_renderer(fmt: str, settings: Settings | None = None, lang: str | None = None) -> Renderer:
    cls = _RENDERERS.get(fmt)
    if cls is None:
        raise ValueError(f"unknown output format: {fmt!r}")
    return cls(settings=settings, lang=lang)


def available_formats() -> tuple[str, ...]:
    return ("html", "text", "markdown", "pdf")


def is_supported(fmt: str) -> bool:
    """Whether the format is supported, including aliases (txt/md)."""
    return fmt in _RENDERERS
