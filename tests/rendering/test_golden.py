# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Per-format golden + determinism (two renders identical)."""

from __future__ import annotations

from pathlib import Path

import pytest

from onot.ingest.excel import parse_excel
from onot.license import resolve
from onot.rendering import render

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "tests" / "fixtures" / "sbom" / "example.spdx.xlsx"
GOLDEN = ROOT / "tests" / "golden"


def _doc():
    return resolve(parse_excel(SAMPLE))


@pytest.mark.parametrize(("fmt", "ext"), [("html", "html"), ("text", "txt"), ("markdown", "md")])
def test_golden_matches(fmt, ext):
    out = render(_doc(), fmt)
    assert out == (GOLDEN / f"slice_notice.{ext}").read_text(encoding="utf-8")


def test_render_deterministic_all_formats():
    doc = _doc()
    for fmt in ("html", "text", "markdown"):
        assert render(doc, fmt) == render(doc, fmt)
