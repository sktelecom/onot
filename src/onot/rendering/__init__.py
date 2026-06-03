# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""고지문 산출물 렌더링."""

from __future__ import annotations

from datetime import datetime

from onot.core.config import Settings
from onot.domain.models import NoticeDocument
from onot.rendering.base import Renderer
from onot.rendering.html import render_html
from onot.rendering.registry import available_formats, get_renderer

__all__ = ["Renderer", "available_formats", "get_renderer", "render", "render_html"]


def render(
    doc: NoticeDocument,
    fmt: str = "html",
    *,
    settings: Settings | None = None,
    lang: str | None = None,
    now: datetime | None = None,
) -> str | bytes:
    return get_renderer(fmt, settings=settings, lang=lang).render(doc, now=now)
