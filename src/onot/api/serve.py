"""사이드카 서버 진입점. FastAPI 앱을 127.0.0.1:PORT에 띄운다(Electron이 spawn).

uvicorn에 import string이 아니라 앱 인스턴스를 직접 넘겨 frozen(PyInstaller) 환경에서도
동적 import 문제 없이 동작한다.
"""

from __future__ import annotations

import argparse

import uvicorn

from onot.api.app import create_app


def main() -> None:
    parser = argparse.ArgumentParser(prog="onot-sidecar")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    uvicorn.run(create_app(), host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
