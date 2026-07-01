# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Renderer ABC + shared Jinja environment.

render() is a pure function with no file I/O. Disk writing is handled by core.writer.OutputWriter.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

import jinja2

from onot.core.config import Settings
from onot.domain.models import NoticeDocument
from onot.rendering.context import build_context
from onot.rendering.filters import anchor, license_links, md_cell, md_code_block, md_inline, oneline
from onot.rendering.i18n import Translator


def make_environment(autoescape_formats: list[str]) -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("onot.rendering", "templates"),
        autoescape=jinja2.select_autoescape(autoescape_formats),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    env.filters["anchor"] = anchor
    env.filters["license_links"] = license_links
    env.filters["md_code_block"] = md_code_block
    env.filters["md_cell"] = md_cell
    env.filters["md_inline"] = md_inline
    env.filters["oneline"] = oneline
    return env


class Renderer(ABC):
    format_id: str
    file_extension: str
    binary: bool = False

    def __init__(self, settings: Settings | None = None, lang: str | None = None) -> None:
        self.settings = settings or Settings()
        self.lang = lang or self.settings.default_lang

    @abstractmethod
    def render(self, doc: NoticeDocument, *, now: datetime | None = None) -> str | bytes: ...


class TemplateRenderer(Renderer):
    """Common skeleton for Jinja-template-based text renderers."""

    template_name: str
    autoescape: list[str] = []

    def __init__(self, settings: Settings | None = None, lang: str | None = None) -> None:
        super().__init__(settings, lang)
        self._env = make_environment(self.autoescape)

    def extra_context(self) -> dict:
        return {}

    def render(self, doc: NoticeDocument, *, now: datetime | None = None) -> str:
        context = build_context(doc, self.settings, now=now)
        template = self._env.get_template(self.template_name)
        return template.render(
            ctx=context,
            doc=doc,
            t=Translator(self.lang),
            **self.extra_context(),
        )
