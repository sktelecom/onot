"""PdfRenderer — HTML을 PDF로 변환(WeasyPrint, onot[pdf] extras).

설치형 데스크톱은 Electron printToPDF를 쓰고, CLI 등 헤드리스 경로에서 이 렌더러를 쓴다.
WeasyPrint 미설치 시 명확한 안내와 함께 실패한다(extras로 격리).
"""

from __future__ import annotations

from datetime import datetime

from onot.core.config import Settings
from onot.domain.models import NoticeDocument
from onot.rendering.base import Renderer
from onot.rendering.html import HtmlRenderer, _theme_css


class PdfRenderer(Renderer):
    format_id = "pdf"
    file_extension = "pdf"
    binary = True

    def __init__(self, settings: Settings | None = None, lang: str | None = None) -> None:
        super().__init__(settings, lang)
        self._html = HtmlRenderer(self.settings, self.lang)

    def render(self, doc: NoticeDocument, *, now: datetime | None = None) -> bytes:
        try:
            from weasyprint import HTML  # noqa: PLC0415 — 선택 의존성 지연 로드
        except ImportError as exc:
            raise RuntimeError(
                "PDF rendering requires WeasyPrint. Install with: pip install 'onot[pdf]'"
            ) from exc
        html = self._html.render(doc, now=now)
        pdf_css = _theme_css(self.settings.theme, "pdf.css")
        document = HTML(string=html)
        return document.write_pdf(stylesheets=_pdf_stylesheets(pdf_css))


def _pdf_stylesheets(pdf_css: str) -> list:
    if not pdf_css:
        return []
    from weasyprint import CSS  # noqa: PLC0415

    return [CSS(string=pdf_css)]
