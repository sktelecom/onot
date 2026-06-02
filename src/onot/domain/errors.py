"""onot 예외 계층. 사용자향 실패는 모두 OnotError 하위로 모은다."""

from __future__ import annotations


class OnotError(Exception):
    """모든 onot 오류의 루트."""


# --- 입력(ingest) -------------------------------------------------------------
class IngestError(OnotError):
    """입력 파싱/적재 단계 오류."""


class UnsupportedFormatError(IngestError):
    """포맷을 감지하지 못했거나 지원하지 않음."""


class ParseError(IngestError):
    """외부 파서 예외를 감싼 파싱 실패(원인 chain 보존)."""


class IngestValidationError(IngestError):
    """문서 검증 실패. 필드별 메시지를 messages에 담는다."""

    def __init__(self, messages: list[str]) -> None:
        self.messages = list(messages)
        super().__init__("; ".join(self.messages) or "ingest validation failed")


# --- 라이선스 ----------------------------------------------------------------
class LicenseError(OnotError):
    """라이선스 해석/조회 오류."""


class ExpressionParseError(LicenseError):
    """라이선스 표현식 파싱 실패."""


class UnknownLicenseError(LicenseError):
    """카탈로그·동봉 어디에도 없는 라이선스."""


class LicenseTextUnavailableError(LicenseError):
    """오프라인이고 캐시·번들에도 전문이 없음."""


# --- 설정 --------------------------------------------------------------------
class ConfigError(OnotError):
    """잘못된 설정."""
