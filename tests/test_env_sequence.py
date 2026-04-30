"""Tests for envoy_cli.env_sequence."""
import pytest

from envoy_cli.vault import save_vault
from envoy_cli.env_sequence import (
    SequenceError,
    get_sequence,
    list_sequences,
    set_sequence,
    remove_sequence,
    resolve_sequence,
)


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    vault = {
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DB_NAME": "mydb"},
        "prod": {"DB_HOST": "prod.db", "DB_PORT": "5432"},
    }
    save_vault(str(path), "secret", vault)
    return str(path)


def test_list_sequences_empty(vault_file):
    result = list_sequences(vault_file, "secret", "dev")
    assert result == []


def test_set_sequence_returns_keys(vault_file):
    keys = ["DB_HOST", "DB_PORT", "DB_NAME"]
    result = set_sequence(vault_file, "secret", "dev", "connection", keys)
    assert result == keys


def test_set_sequence_persisted(vault_file):
    set_sequence(vault_file, "secret", "dev", "connection", ["DB_HOST", "DB_PORT"])
    result = get_sequence(vault_file, "secret", "dev", "connection")
    assert result == ["DB_HOST", "DB_PORT"]


def test_list_sequences_after_set(vault_file):
    set_sequence(vault_file, "secret", "dev", "connection", ["DB_HOST"])
    set_sequence(vault_file, "secret", "dev", "auth", ["DB_NAME"])
    result = list_sequences(vault_file, "secret", "dev")
    assert result == ["auth", "connection"]


def test_set_sequence_unknown_profile_raises(vault_file):
    with pytest.raises(SequenceError, match="Profile 'staging' not found"):
        set_sequence(vault_file, "secret", "staging", "seq", [])


def test_set_sequence_unknown_key_raises(vault_file):
    with pytest.raises(SequenceError, match="Key 'UNKNOWN' not found"):
        set_sequence(vault_file, "secret", "dev", "seq", ["UNKNOWN"])


def test_set_sequence_duplicate_keys_raises(vault_file):
    with pytest.raises(SequenceError, match="duplicate"):
        set_sequence(vault_file, "secret", "dev", "seq", ["DB_HOST", "DB_HOST"])


def test_remove_sequence_returns_true(vault_file):
    set_sequence(vault_file, "secret", "dev", "connection", ["DB_HOST"])
    result = remove_sequence(vault_file, "secret", "dev", "connection")
    assert result is True


def test_remove_sequence_removes_entry(vault_file):
    set_sequence(vault_file, "secret", "dev", "connection", ["DB_HOST"])
    remove_sequence(vault_file, "secret", "dev", "connection")
    assert get_sequence(vault_file, "secret", "dev", "connection") == []


def test_remove_sequence_missing_returns_false(vault_file):
    result = remove_sequence(vault_file, "secret", "dev", "nonexistent")
    assert result is False


def test_resolve_sequence_returns_key_value_pairs(vault_file):
    set_sequence(vault_file, "secret", "dev", "conn", ["DB_HOST", "DB_PORT"])
    result = resolve_sequence(vault_file, "secret", "dev", "conn")
    assert result == [
        {"key": "DB_HOST", "value": "localhost"},
        {"key": "DB_PORT", "value": "5432"},
    ]


def test_resolve_sequence_missing_raises(vault_file):
    with pytest.raises(SequenceError, match="Sequence 'missing' not found"):
        resolve_sequence(vault_file, "secret", "dev", "missing")


def test_set_sequence_overwrites_existing(vault_file):
    set_sequence(vault_file, "secret", "dev", "conn", ["DB_HOST"])
    set_sequence(vault_file, "secret", "dev", "conn", ["DB_PORT", "DB_NAME"])
    result = get_sequence(vault_file, "secret", "dev", "conn")
    assert result == ["DB_PORT", "DB_NAME"]
