"""Tests for envoy_cli.pin module."""

import pytest
from click.testing import CliRunner
from envoy_cli.vault import save_vault, load_vault
from envoy_cli.pin import (
    pin_key, unpin_key, get_pinned_keys, is_pinned, apply_pins, PinError
)
from envoy_cli.commands.pin_cmd import pin


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    data = {
        "production": {"DB_HOST": "prod-db", "SECRET": "abc123", "PORT": "5432"},
        "staging": {"DB_HOST": "stage-db", "SECRET": "xyz789"},
    }
    save_vault(path, "pass", data)
    return path


def test_pin_key_success(vault_file):
    pins = pin_key(vault_file, "pass", "production", "SECRET")
    assert "SECRET" in pins


def test_pin_key_persisted(vault_file):
    pin_key(vault_file, "pass", "production", "DB_HOST")
    vault = load_vault(vault_file, "pass")
    assert "DB_HOST" in get_pinned_keys(vault, "production")


def test_pin_multiple_keys_sorted(vault_file):
    pin_key(vault_file, "pass", "production", "SECRET")
    pins = pin_key(vault_file, "pass", "production", "DB_HOST")
    assert pins == sorted(pins)


def test_pin_duplicate_no_duplicates(vault_file):
    pin_key(vault_file, "pass", "production", "SECRET")
    pins = pin_key(vault_file, "pass", "production", "SECRET")
    assert pins.count("SECRET") == 1


def test_pin_nonexistent_profile_raises(vault_file):
    with pytest.raises(PinError, match="Profile"):
        pin_key(vault_file, "pass", "ghost", "KEY")


def test_pin_nonexistent_key_raises(vault_file):
    with pytest.raises(PinError, match="Key"):
        pin_key(vault_file, "pass", "production", "NONEXISTENT")


def test_unpin_key_removes(vault_file):
    pin_key(vault_file, "pass", "production", "SECRET")
    pins = unpin_key(vault_file, "pass", "production", "SECRET")
    assert "SECRET" not in pins


def test_unpin_nonexistent_key_is_safe(vault_file):
    pins = unpin_key(vault_file, "pass", "production", "NEVER_PINNED")
    assert isinstance(pins, list)


def test_is_pinned_true(vault_file):
    pin_key(vault_file, "pass", "production", "PORT")
    vault = load_vault(vault_file, "pass")
    assert is_pinned(vault, "production", "PORT") is True


def test_is_pinned_false(vault_file):
    vault = load_vault(vault_file, "pass")
    assert is_pinned(vault, "production", "DB_HOST") is False


def test_apply_pins_preserves_pinned():
    base = {"A": "original", "B": "base_b"}
    incoming = {"A": "overwritten", "B": "new_b", "C": "new_c"}
    result = apply_pins(base, incoming, pinned_keys=["A"])
    assert result["A"] == "original"
    assert result["B"] == "new_b"
    assert result["C"] == "new_c"


def test_apply_pins_no_pins():
    base = {"A": "original"}
    incoming = {"A": "overwritten"}
    result = apply_pins(base, incoming, pinned_keys=[])
    assert result["A"] == "overwritten"


def test_cmd_list_pins(vault_file):
    runner = CliRunner()
    pin_key(vault_file, "pass", "production", "SECRET")
    result = runner.invoke(
        pin, ["list", "production", "--vault", vault_file, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "SECRET" in result.output


def test_cmd_list_pins_empty(vault_file):
    runner = CliRunner()
    result = runner.invoke(
        pin, ["list", "staging", "--vault", vault_file, "--password", "pass"]
    )
    assert result.exit_code == 0
    assert "No pinned" in result.output
