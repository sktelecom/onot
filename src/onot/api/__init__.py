# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""FastAPI 사이드카 (Electron 데스크톱 + 향후 정적 SaaS 백엔드 공용)."""

from onot.api.app import create_app

__all__ = ["create_app"]
