"""onot 도메인 모델 (순수 Pydantic, 외부 의존 없음)."""

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
