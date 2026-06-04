# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Sidecar entry point: delegates to uvicorn with the correct host/port (no real server started)."""

from __future__ import annotations

import onot.api.serve as serve


def test_main_invokes_uvicorn_with_args(monkeypatch):
    captured = {}
    monkeypatch.setattr(serve.uvicorn, "run", lambda app, **kw: captured.update({"app": app, **kw}))
    monkeypatch.setattr("sys.argv", ["onot-sidecar", "--port", "9999", "--host", "127.0.0.1"])
    serve.main()
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 9999
    assert captured["app"] is not None
