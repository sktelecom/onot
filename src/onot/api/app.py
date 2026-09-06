# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""FastAPI app factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from onot import __version__
from onot.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="onot", version=__version__)
    # Allow calls from the local frontend (including the dev server). The sidecar binds to 127.0.0.1.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_methods=["*"],
        allow_headers=["*"],
        # The desktop app runs on a different origin from the sidecar, and a cross-origin
        # response hides every header but the safelisted few. Without this the frontend cannot
        # read the filename the render endpoint chose and falls back to a generic one.
        expose_headers=["Content-Disposition"],
    )
    app.include_router(router)
    return app


app = create_app()
