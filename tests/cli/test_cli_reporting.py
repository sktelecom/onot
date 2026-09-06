# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""How the CLI reports a run: the warning summary, --quiet and --json."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from onot.cli.main import app
from onot.cli.warnings import summarize

ROOT = Path(__file__).resolve().parents[2]
SPDX_JSON = ROOT / "tests" / "fixtures" / "sbom" / "example.spdx.json"

runner = CliRunner()


def _sbom_with_warnings(tmp_path: Path) -> Path:
    """Two packages with no license information, which the resolver warns about."""
    packages = [
        {
            "SPDXID": f"SPDXRef-p{index}",
            "name": f"p{index}",
            "downloadLocation": "NOASSERTION",
            "licenseConcluded": "NOASSERTION",
            "licenseDeclared": "NOASSERTION",
            "copyrightText": "NOASSERTION",
            "filesAnalyzed": False,
        }
        for index in range(2)
    ]
    sbom = tmp_path / "w.spdx.json"
    sbom.write_text(
        json.dumps(
            {
                "spdxVersion": "SPDX-2.3",
                "dataLicense": "CC0-1.0",
                "SPDXID": "SPDXRef-DOCUMENT",
                "name": "w",
                "documentNamespace": "https://example.com/w",
                "creationInfo": {"created": "2024-01-01T00:00:00Z", "creators": ["Tool: t"]},
                "packages": packages,
                "relationships": [
                    {
                        "spdxElementId": "SPDXRef-DOCUMENT",
                        "relatedSpdxElement": package["SPDXID"],
                        "relationshipType": "DESCRIBES",
                    }
                    for package in packages
                ],
            }
        ),
        encoding="utf-8",
    )
    return sbom


def test_summarize_groups_by_kind():
    assert summarize([]) == ""
    assert summarize(["no license information for a 1"]) == (
        "1 warning (1 components without license information)"
    )
    assert summarize(
        [
            "no license information for a 1",
            "no license information for b 2",
            "missing license text for MIT",
            "something else entirely",
        ]
    ) == (
        "4 warnings (2 components without license information, "
        "1 licenses without bundled text, 1 other)"
    )


def test_warnings_end_with_a_count_by_kind(tmp_path):
    sbom = _sbom_with_warnings(tmp_path)
    result = runner.invoke(app, ["generate", "-i", str(sbom), "--output-dir", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "no license information for p0" in result.output
    assert "2 warnings (2 components without license information)" in result.output


def test_quiet_drops_the_warnings_but_keeps_the_result(tmp_path):
    sbom = _sbom_with_warnings(tmp_path)
    result = runner.invoke(
        app, ["generate", "-i", str(sbom), "--output-dir", str(tmp_path), "--quiet"]
    )
    assert result.exit_code == 0, result.output
    assert "warning: " not in result.output
    assert "no license information" not in result.output
    assert "wrote " in result.output


def test_json_reports_the_files_and_the_warnings(tmp_path):
    sbom = _sbom_with_warnings(tmp_path)
    result = runner.invoke(
        app, ["generate", "-i", str(sbom), "-f", "html", "--output-dir", str(tmp_path), "--json"]
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.stdout)
    assert payload["product"] == "w"
    assert [entry["format"] for entry in payload["written"]] == ["html"]
    assert Path(payload["written"][0]["path"]).exists()
    assert len(payload["warnings"]) == 2
    # Machine output has to parse on its own, so nothing else may share stdout.
    assert "wrote " not in result.stdout


def test_json_and_stdout_together_are_refused():
    result = runner.invoke(
        app, ["generate", "-i", str(SPDX_JSON), "-f", "text", "--stdout", "--json"]
    )
    assert result.exit_code == 1
    assert "both write to stdout" in result.output
