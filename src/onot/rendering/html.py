"""HtmlRenderer — self-contained HTML(테마 CSS 인라인, autoescape, 라이선스 앵커)."""

from __future__ import annotations

from datetime import datetime
from functools import cache
from importlib.resources import files

from onot.domain.models import NoticeDocument
from onot.rendering.base import TemplateRenderer


@cache
def _theme_css(theme: str, name: str) -> str:
    resource = files("onot.rendering") / "themes" / theme / name
    try:
        return resource.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return ""


class HtmlRenderer(TemplateRenderer):
    format_id = "html"
    file_extension = "html"
    template_name = "html/notice.html.jinja"
    autoescape = ["html", "jinja"]

    def extra_context(self) -> dict:
        return {"css": _theme_css(self.settings.theme, "notice.css")}


def render_html(
    doc: NoticeDocument,
    *,
    now: datetime | None = None,
    settings=None,
    lang: str | None = None,
) -> str:
    return HtmlRenderer(settings=settings, lang=lang).render(doc, now=now)
