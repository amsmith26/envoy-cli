"""Tests for envoy_cli.template and template_cmd."""
from __future__ import annotations
import json
import os
import pytest
from click.testing import CliRunner
from envoy_cli.template import render_template, collect_placeholders
from envoy_cli.vault import save_vault
from envoy_cli.commands.template_cmd import template


ENV = {"APP_HOST": "localhost", "APP_PORT": "8080", "SECRET": "s3cr3t"}


def test_render_basic():
    tmpl = "host={{ APP_HOST }} port={{ APP_PORT }}"
    result = render_template(tmpl, ENV)
    assert result == "host=localhost port=8080"


def test_render_missing_key_lenient():
    tmpl = "value={{MISSING}}"
    result = render_template(tmpl, ENV, strict=False)
    assert "{{MISSING}}" in result


def test_render_missing_key_strict():
    tmpl = "value={{MISSING}}"
    with pytest.raises(KeyError, match="MISSING"):
        render_template(tmpl, ENV, strict=True)


def test_render_no_placeholders():
    tmpl = "plain text"
    assert render_template(tmpl, ENV) == "plain text"


def test_collect_placeholders():
    tmpl = "{{B}} and {{A}} and {{B}}"
    keys = collect_placeholders(tmpl)
    assert keys == ["A", "B"]


def test_collect_placeholders_empty():
    assert collect_placeholders("no placeholders here") == []


@pytest.fixture()
def workspace(tmp_path):
    vault_file = tmp_path / "vault.env.vault"
    save_vault(str(vault_file), {"prod": ENV}, "pass")
    tmpl_file = tmp_path / "config.tmpl"
    tmpl_file.write_text("HOST={{APP_HOST}}\nPORT={{APP_PORT}}\n")
    return tmp_path, str(vault_file), str(tmpl_file)


def test_cmd_render_stdout(workspace):
    tmp_path, vault_file, tmpl_file = workspace
    runner = CliRunner()
    result = runner.invoke(template, ["render", tmpl_file, "--vault", vault_file, "--profile", "prod", "--password", "pass"])
    assert result.exit_code == 0
    assert "HOST=localhost" in result.output
    assert "PORT=8080" in result.output


def test_cmd_render_to_file(workspace, tmp_path):
    _, vault_file, tmpl_file = workspace
    out_file = str(tmp_path / "out.txt")
    runner = CliRunner()
    result = runner.invoke(template, ["render", tmpl_file, "--vault", vault_file, "--profile", "prod", "--password", "pass", "-o", out_file])
    assert result.exit_code == 0
    assert os.path.exists(out_file)
    assert "HOST=localhost" in open(out_file).read()


def test_cmd_render_missing_profile(workspace):
    _, vault_file, tmpl_file = workspace
    runner = CliRunner()
    result = runner.invoke(template, ["render", tmpl_file, "--vault", vault_file, "--profile", "ghost", "--password", "pass"])
    assert result.exit_code != 0


def test_cmd_inspect(workspace):
    _, _, tmpl_file = workspace
    runner = CliRunner()
    result = runner.invoke(template, ["inspect", tmpl_file])
    assert result.exit_code == 0
    assert "APP_HOST" in result.output
    assert "APP_PORT" in result.output
