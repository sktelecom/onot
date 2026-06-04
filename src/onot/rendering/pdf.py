# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""PdfRenderer — converts HTML to PDF (WeasyPrint, onot[pdf] extras).

The installable desktop uses Electron printToPDF; this renderer is used on headless paths
such as the CLI. If WeasyPrint is not installed, it fails with a clear message (isolated via extras).
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
            from weasyprint import HTML  # noqa: PLC0415 — lazy-load optional dependency
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
