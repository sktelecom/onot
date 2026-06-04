# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""onot exception hierarchy. All user-facing failures derive from OnotError."""

from __future__ import annotations


class OnotError(Exception):
    """Root of all onot errors."""


# --- ingest -------------------------------------------------------------------
class IngestError(OnotError):
    """Error during the input parsing/loading stage."""


class UnsupportedFormatError(IngestError):
    """Format could not be detected or is not supported."""


class ParseError(IngestError):
    """Parse failure wrapping an external parser exception (preserves cause chain)."""


class IngestValidationError(IngestError):
    """Document validation failure. Per-field messages are stored in messages."""

    def __init__(self, messages: list[str]) -> None:
        self.messages = list(messages)
        super().__init__("; ".join(self.messages) or "ingest validation failed")


# --- license ------------------------------------------------------------------
class LicenseError(OnotError):
    """License resolution/lookup error."""


class ExpressionParseError(LicenseError):
    """License expression parse failure."""


class UnknownLicenseError(LicenseError):
    """License found neither in the catalog nor embedded in the document."""


class LicenseTextUnavailableError(LicenseError):
    """Offline and the full text is absent from both cache and bundle."""


# --- config -------------------------------------------------------------------
class ConfigError(OnotError):
    """Invalid configuration."""
