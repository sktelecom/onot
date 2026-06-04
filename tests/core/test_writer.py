# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""OutputWriter: text/binary writing, parent directory creation."""

from __future__ import annotations

from onot.core.writer import OutputWriter


def test_write_text(tmp_path):
    path = OutputWriter().write("hello", tmp_path / "a.txt")
    assert path.read_text(encoding="utf-8") == "hello"


def test_write_bytes(tmp_path):
    path = OutputWriter().write(b"%PDF-1.7", tmp_path / "a.pdf")
    assert path.read_bytes() == b"%PDF-1.7"


def test_creates_parent_dirs(tmp_path):
    path = OutputWriter().write("x", tmp_path / "deep" / "nested" / "c.txt")
    assert path.exists()
