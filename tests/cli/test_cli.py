"""CLI: 다중 포맷, 자동감지, 언어, stdout, formats/version, 오류 종료 코드."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from onot.cli.main import app

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "tests" / "fixtures" / "sbom" / "example.spdx.xlsx"
SPDX_JSON = ROOT / "tests" / "fixtures" / "sbom" / "example.spdx.json"

runner = CliRunner()


def test_generate_multiple_formats(tmp_path):
    result = runner.invoke(
        app,
        ["generate", "-i", str(SAMPLE), "-f", "html", "-f", "text", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert len(list(tmp_path.glob("*.html"))) == 1
    assert len(list(tmp_path.glob("*.txt"))) == 1


def test_generate_autodetects_spdx_json(tmp_path):
    result = runner.invoke(
        app, ["generate", "-i", str(SPDX_JSON), "-f", "markdown", "--output-dir", str(tmp_path)]
    )
    assert result.exit_code == 0, result.output
    md = next(iter(tmp_path.glob("*.md")))
    assert "example-product" in md.read_text(encoding="utf-8")


def test_generate_lang_ko_stdout():
    result = runner.invoke(
        app, ["generate", "-i", str(SPDX_JSON), "-f", "text", "--stdout", "--lang", "ko"]
    )
    assert result.exit_code == 0, result.output
    assert "오픈소스 고지" in result.output


def test_stdout_rejects_multiple_formats():
    result = runner.invoke(
        app, ["generate", "-i", str(SPDX_JSON), "-f", "html", "-f", "text", "--stdout"]
    )
    assert result.exit_code == 1


def test_stdout_rejects_binary_pdf():
    result = runner.invoke(app, ["generate", "-i", str(SPDX_JSON), "-f", "pdf", "--stdout"])
    assert result.exit_code == 1


def test_unknown_format_clean_exit_2(tmp_path):
    result = runner.invoke(
        app, ["generate", "-i", str(SPDX_JSON), "-f", "xml", "--output-dir", str(tmp_path)]
    )
    assert result.exit_code == 2
    assert "unknown output format" in result.output
    assert "Traceback" not in result.output  # 트레이스백 노출 없이 깔끔히 종료


def test_format_aliases_accepted(tmp_path):
    result = runner.invoke(
        app,
        ["generate", "-i", str(SPDX_JSON), "-f", "md", "-f", "txt", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert len(list(tmp_path.glob("*.md"))) == 1
    assert len(list(tmp_path.glob("*.txt"))) == 1


def test_invalid_lang_exit_4(tmp_path):
    result = runner.invoke(
        app, ["generate", "-i", str(SPDX_JSON), "--lang", "xx", "--output-dir", str(tmp_path)]
    )
    assert result.exit_code == 4


def test_strict_unknown_license_exit_3(tmp_path):
    sbom = tmp_path / "u.spdx.json"
    sbom.write_text(
        json.dumps(
            {
                "spdxVersion": "SPDX-2.3",
                "dataLicense": "CC0-1.0",
                "SPDXID": "SPDXRef-DOCUMENT",
                "name": "u",
                "documentNamespace": "https://example.com/u",
                "creationInfo": {"created": "2024-01-01T00:00:00Z", "creators": ["Tool: t"]},
                "packages": [
                    {
                        "SPDXID": "SPDXRef-p",
                        "name": "p",
                        "downloadLocation": "NOASSERTION",
                        "licenseConcluded": "LicenseRef-Unknown",
                        "copyrightText": "NOASSERTION",
                        "filesAnalyzed": False,
                    }
                ],
                "relationships": [
                    {
                        "spdxElementId": "SPDXRef-DOCUMENT",
                        "relatedSpdxElement": "SPDXRef-p",
                        "relationshipType": "DESCRIBES",
                    }
                ],
            }
        )
    )
    result = runner.invoke(
        app, ["generate", "-i", str(sbom), "--strict", "--output-dir", str(tmp_path)]
    )
    assert result.exit_code == 3


def test_online_mode_smoke(tmp_path):
    # --online은 fetcher/cache를 주입하지만 번들 라이선스는 네트워크 없이 처리된다
    result = runner.invoke(
        app,
        ["generate", "-i", str(SPDX_JSON), "-f", "text", "--online", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output


def test_unsupported_input_exit_code_2(tmp_path):
    bad = tmp_path / "x.txt"
    bad.write_text("not an sbom")
    result = runner.invoke(app, ["generate", "-i", str(bad), "--output-dir", str(tmp_path)])
    assert result.exit_code == 2


def test_config_yaml_company(tmp_path):
    config = tmp_path / "onot.yaml"
    config.write_text(
        yaml.safe_dump({"company": {"organization": "SKT", "contact_email": "oss@skt.example"}})
    )
    result = runner.invoke(
        app,
        [
            "generate",
            "-i",
            str(SPDX_JSON),
            "-f",
            "html",
            "--output-dir",
            str(tmp_path),
            "--config",
            str(config),
        ],
    )
    assert result.exit_code == 0, result.output
    html = next(iter(tmp_path.glob("*.html")))
    assert "oss@skt.example" in html.read_text(encoding="utf-8")


def test_formats_command():
    result = runner.invoke(app, ["formats"])
    assert result.exit_code == 0
    assert "html" in result.output
    assert "pdf" in result.output


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.output.strip().startswith("2.")
