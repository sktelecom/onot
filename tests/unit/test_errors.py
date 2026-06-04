# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""Exception hierarchy test."""

from __future__ import annotations

from onot.domain.errors import (
    IngestError,
    IngestValidationError,
    LicenseError,
    OnotError,
    UnknownLicenseError,
    UnsupportedFormatError,
)


def test_hierarchy():
    assert issubclass(IngestError, OnotError)
    assert issubclass(UnsupportedFormatError, IngestError)
    assert issubclass(UnknownLicenseError, LicenseError)
    assert issubclass(LicenseError, OnotError)


def test_ingest_validation_error_messages():
    err = IngestValidationError(["bad field a", "missing b"])
    assert err.messages == ["bad field a", "missing b"]
    assert "bad field a" in str(err)
    assert "missing b" in str(err)


def test_ingest_validation_error_empty():
    err = IngestValidationError([])
    assert err.messages == []
    assert str(err) == "ingest validation failed"
