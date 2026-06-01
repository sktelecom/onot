"""TextRenderer — 플레인 텍스트 고지문."""

from __future__ import annotations

from onot.rendering.base import TemplateRenderer


class TextRenderer(TemplateRenderer):
    format_id = "text"
    file_extension = "txt"
    template_name = "text/notice.txt.jinja"
    autoescape: list[str] = []
