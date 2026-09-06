# SPDX-FileCopyrightText: Kakao Corp. and SK telecom Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""onot init: the configuration template, which used to exist only as fields in config.py."""

from __future__ import annotations

import yaml
from typer.testing import CliRunner

from onot.cli.main import app
from onot.core.config import CompanyConfig, Settings, load_settings

runner = CliRunner()


def test_init_writes_a_file_the_loader_accepts(tmp_path):
    target = tmp_path / "onot.yaml"
    result = runner.invoke(app, ["init", "--output", str(target)])
    assert result.exit_code == 0, result.output
    assert target.exists()

    # The template has to load, or it teaches the wrong shape.
    settings = load_settings(target)
    assert isinstance(settings, Settings)
    assert settings.default_lang == "en"


def test_the_template_covers_every_company_field(tmp_path):
    """A reader should not have to open config.py to learn the field names."""
    target = tmp_path / "onot.yaml"
    runner.invoke(app, ["init", "--output", str(target)])
    data = yaml.safe_load(target.read_text(encoding="utf-8"))
    assert set(data["company"]) == set(CompanyConfig.model_fields)


def test_init_refuses_to_overwrite_without_force(tmp_path):
    target = tmp_path / "onot.yaml"
    target.write_text("company:\n  organization: Mine\n", encoding="utf-8")

    result = runner.invoke(app, ["init", "--output", str(target)])
    assert result.exit_code == 1
    assert "already exists" in result.output
    assert "Mine" in target.read_text(encoding="utf-8")

    forced = runner.invoke(app, ["init", "--output", str(target), "--force"])
    assert forced.exit_code == 0
    assert "Mine" not in target.read_text(encoding="utf-8")
