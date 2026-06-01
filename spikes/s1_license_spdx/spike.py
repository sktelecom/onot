"""S1 스파이크 — license-expression / spdx-tools 실제 API 형태 검증.

플랜 §3(license)·§2(ingest)가 가정하는 API가 실제로 동작하는지 확인한다.
PASS/FAIL을 출력하고, 실패 시 비-0 종료.
"""

from __future__ import annotations

import sys
import traceback

results: list[tuple[str, bool, str]] = []


def check(name: str, fn) -> None:
    try:
        detail = fn()
        results.append((name, True, str(detail)))
    except Exception as exc:  # noqa: BLE001
        results.append((name, False, f"{type(exc).__name__}: {exc}"))
        traceback.print_exc()


# --- license-expression -------------------------------------------------------
def le_parse_decompose():
    from license_expression import get_spdx_licensing

    lic = get_spdx_licensing()
    expr = "Apache-2.0 OR (MIT AND BSD-3-Clause)"
    parsed = lic.parse(expr)
    syms = lic.license_symbols(parsed, unique=True, decompose=True)
    ids = sorted(str(s) for s in syms)
    assert ids == ["Apache-2.0", "BSD-3-Clause", "MIT"], ids
    return ids


def le_with_exception():
    from license_expression import get_spdx_licensing

    lic = get_spdx_licensing()
    parsed = lic.parse("GPL-2.0-only WITH Classpath-exception-2.0")
    syms = [str(s) for s in lic.license_symbols(parsed, unique=True, decompose=True)]
    # decompose는 license + exception 심볼을 분리해 노출
    return syms


def le_plus_operator():
    from license_expression import get_spdx_licensing

    lic = get_spdx_licensing()
    parsed = lic.parse("GPL-2.0+")
    return str(parsed)


def le_validate_unknown():
    from license_expression import get_spdx_licensing

    lic = get_spdx_licensing()
    v = lic.validate("Apache-2.0 OR NoSuchLicense-9.9")
    # ExpressionInfo: errors / unknown_licenses 등 필드 확인
    return {
        "errors": getattr(v, "errors", None),
        "unknown": getattr(v, "unknown_license_keys", getattr(v, "unknown_licenses", None)),
    }


# --- spdx-tools ---------------------------------------------------------------
SPDX_FIXTURE = "spikes/s1_license_spdx/minimal_spdx23.json"


def spdx_parse_rdf():
    from spdx_tools.spdx.parser.parse_anything import parse_file

    doc = parse_file(SPDX_FIXTURE)
    ci = doc.creation_info
    pkgs = doc.packages
    out = {
        "doc_name": getattr(ci, "name", None),
        "spdx_version": getattr(ci, "spdx_version", None),
        "n_packages": len(pkgs),
        "creators": [str(c) for c in getattr(ci, "creators", [])][:3],
    }
    if pkgs:
        p = pkgs[0]
        out["pkg0"] = {
            "name": p.name,
            "version": getattr(p, "version", None),
            "license_concluded": str(getattr(p, "license_concluded", None)),
            "license_declared": str(getattr(p, "license_declared", None)),
            "copyright": str(getattr(p, "copyright_text", None))[:40],
            "download": str(getattr(p, "download_location", None))[:40],
        }
    out["extracted_licensing_info"] = len(getattr(doc, "extracted_licensing_info", []))
    return out


def spdx_validate():
    from spdx_tools.spdx.parser.parse_anything import parse_file
    from spdx_tools.spdx.validation.document_validator import (
        validate_full_spdx_document,
    )

    doc = parse_file(SPDX_FIXTURE)
    messages = validate_full_spdx_document(doc)
    return {"n_validation_messages": len(messages)}


check("license-expression: parse+decompose nested", le_parse_decompose)
check("license-expression: WITH exception", le_with_exception)
check("license-expression: + operator", le_plus_operator)
check("license-expression: validate unknown", le_validate_unknown)
check("spdx-tools: parse RDF (2.3)", spdx_parse_rdf)
check("spdx-tools: validate_full_spdx_document", spdx_validate)

print("\n==== S1 RESULTS ====")
ok = True
for name, passed, detail in results:
    flag = "PASS" if passed else "FAIL"
    if not passed:
        ok = False
    print(f"[{flag}] {name}\n        {detail}")

sys.exit(0 if ok else 1)
