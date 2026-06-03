# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from onot.api.app import create_app


@pytest.fixture(scope="session")
def client():
    return TestClient(create_app())
