# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""onot domain models (pure Pydantic, no external dependencies)."""

from onot.domain.errors import (
    ConfigError,
    ExpressionParseError,
    IngestError,
    IngestValidationError,
    LicenseError,
    LicenseTextUnavailableError,
    OnotError,
    ParseError,
    UnknownLicenseError,
    UnsupportedFormatError,
)
from onot.domain.models import (
    Copyright,
    CreationInfo,
    License,
    LicenseExpression,
    LicenseRef,
    NoticeDocument,
    Package,
    PackageRef,
)

__all__ = [
    "ConfigError",
    "Copyright",
    "CreationInfo",
    "ExpressionParseError",
    "IngestError",
    "IngestValidationError",
    "License",
    "LicenseError",
    "LicenseExpression",
    "LicenseRef",
    "LicenseTextUnavailableError",
    "NoticeDocument",
    "OnotError",
    "Package",
    "PackageRef",
    "ParseError",
    "UnknownLicenseError",
    "UnsupportedFormatError",
]
