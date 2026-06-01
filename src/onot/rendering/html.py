"""HtmlRenderer (M0.5 슬라이스).

Jinja2 + autoescape로 self-contained HTML 고지문을 생성한다. 파일 I/O 없이 문자열 반환.
M4에서 Renderer ABC, 테마 CSS 분리, license_links 앵커 필터, text/md/pdf로 확장된다.
"""

from __future__ import annotations

from datetime import datetime

import jinja2

from onot.domain.models import NoticeDocument

_env = jinja2.Environment(
    loader=jinja2.PackageLoader("onot.rendering", "templates"),
    autoescape=jinja2.select_autoescape(["html", "jinja"]),
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_html(doc: NoticeDocument, *, now: datetime | None = None) -> str:
    """고지문 HTML 문자열을 반환. now를 주면 생성일이 표기되어 골든 테스트가 결정적."""
    template = _env.get_template("notice.html.jinja")
    generated = now.strftime("%Y-%m-%d") if now is not None else ""
    return template.render(doc=doc, generated=generated)
