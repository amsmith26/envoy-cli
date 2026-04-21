"""Tests for envoy_cli.env_docs and the doc CLI commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envoy_cli.vault import save_vault
from envoy_cli.env_docs import DocError, get_doc, list_docs, remove_doc, set_doc
from envoy_cli.commands.doc_cmd import doc


PASSWORD = "testpass"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "vault.env.vault")
    save_vault(path, PASSWORD, {"prod": {"API_KEY": "secret", "DEBUG": "false"}})
    return path


# --- unit tests ---

def test_set_doc_returns_text(vault_file):
    result = set_doc(vault_file, PASSWORD, "prod", "API_KEY", "The production API key.")
    assert result == "The production API key."


def test_get_doc_after_set(vault_file):
    set_doc(vault_file, PASSWORD, "prod", "API_KEY", "My doc.")
    assert get_doc(vault_file, PASSWORD, "prod", "API_KEY") == "My doc."


def test_get_doc_missing_returns_none(vault_file):
    assert get_doc(vault_file, PASSWORD, "prod", "DEBUG") is None


def test_set_doc_unknown_key_raises(vault_file):
    with pytest.raises(DocError, match="UNKNOWN"):
        set_doc(vault_file, PASSWORD, "prod", "UNKNOWN", "oops")


def test_remove_doc_returns_true_when_present(vault_file):
    set_doc(vault_file, PASSWORD, "prod", "DEBUG", "Enable debug mode.")
    assert remove_doc(vault_file, PASSWORD, "prod", "DEBUG") is True


def test_remove_doc_returns_false_when_absent(vault_file):
    assert remove_doc(vault_file, PASSWORD, "prod", "DEBUG") is False


def test_list_docs_empty(vault_file):
    assert list_docs(vault_file, PASSWORD, "prod") == {}


def test_list_docs_after_multiple_sets(vault_file):
    set_doc(vault_file, PASSWORD, "prod", "API_KEY", "Key A.")
    set_doc(vault_file, PASSWORD, "prod", "DEBUG", "Key B.")
    docs = list_docs(vault_file, PASSWORD, "prod")
    assert docs == {"API_KEY": "Key A.", "DEBUG": "Key B."}


# --- CLI tests ---

@pytest.fixture()
def workspace(tmp_path):
    path = str(tmp_path / "vault.env.vault")
    save_vault(path, PASSWORD, {"prod": {"TOKEN": "abc"}})
    return path


@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_set_and_get(workspace, runner):
    result = runner.invoke(
        doc, ["--vault", workspace, "--password", PASSWORD, "set", "prod", "TOKEN", "Auth token."]
    )
    assert result.exit_code == 0
    result = runner.invoke(
        doc, ["--vault", workspace, "--password", PASSWORD, "get", "prod", "TOKEN"]
    )
    assert "Auth token." in result.output


def test_cli_list_no_docs(workspace, runner):
    result = runner.invoke(
        doc, ["--vault", workspace, "--password", PASSWORD, "list", "prod"]
    )
    assert "No documentation" in result.output


def test_cli_remove_existing(workspace, runner):
    runner.invoke(
        doc, ["--vault", workspace, "--password", PASSWORD, "set", "prod", "TOKEN", "x"]
    )
    result = runner.invoke(
        doc, ["--vault", workspace, "--password", PASSWORD, "remove", "prod", "TOKEN"]
    )
    assert "removed" in result.output
