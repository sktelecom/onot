# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""FastAPI 앱 팩토리."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from onot import __version__
from onot.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="onot", version=__version__)
    # 로컬 프론트엔드(개발 서버 포함)에서의 호출 허용. 사이드카는 127.0.0.1 바인딩.
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
