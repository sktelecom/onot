# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""FastAPI sidecar (shared by the Electron desktop and a future static SaaS backend)."""

from onot.api.app import create_app

__all__ = ["create_app"]
