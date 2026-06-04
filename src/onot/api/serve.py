# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Sidecar server entry point. Runs the FastAPI app on 127.0.0.1:PORT (spawned by Electron).

The app instance is passed directly to uvicorn instead of an import string, so it works
without dynamic-import issues even in a frozen (PyInstaller) environment.
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
