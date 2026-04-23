"""Tests for envoy_cli.env_cast."""

import pytest

from envoy_cli.env_cast import (
    CastError,
    apply_casts,
    cast_value,
    get_cast,
    list_casts,
    remove_cast,
    set_cast,
)
from envoy_cli.vault import save_vault

PASSWORD = "test-secret"


@pytest.fixture
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    save_vault(path, PASSWORD, {"production": {"PORT": "8080", "DEBUG": "true", "RATIO": "3.14"}})
    return path


# --- cast_value ---

def test_cast_value_str():
    assert cast_value("hello", "str") == "hello"


def test_cast_value_int():
    assert cast_value("42", "int") == 42


def test_cast_value_float():
    assert cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_value_bool_true():
    for val in ("true", "1", "yes"):
        assert cast_value(val, "bool") is True


def test_cast_value_bool_false():
    for val in ("false", "0", "no"):
        assert cast_value(val, "bool") is False


def test_cast_value_invalid_int_raises():
    with pytest.raises(CastError, match="Cannot cast"):
        cast_value("abc", "int")


def test_cast_value_invalid_bool_raises():
    with pytest.raises(CastError, match="Cannot cast"):
        cast_value("maybe", "bool")


def test_cast_value_unsupported_type_raises():
    with pytest.raises(CastError, match="Unsupported type"):
        cast_value("val", "list")


# --- set_cast / get_cast ---

def test_set_cast_returns_type(vault_file):
    result = set_cast(vault_file, PASSWORD, "production", "PORT", "int")
    assert result == "int"


def test_get_cast_after_set(vault_file):
    set_cast(vault_file, PASSWORD, "production", "PORT", "int")
    assert get_cast(vault_file, PASSWORD, "production", "PORT") == "int"


def test_get_cast_missing_returns_none(vault_file):
    assert get_cast(vault_file, PASSWORD, "production", "PORT") is None


def test_set_cast_unknown_profile_raises(vault_file):
    with pytest.raises(CastError, match="Profile"):
        set_cast(vault_file, PASSWORD, "staging", "PORT", "int")


def test_set_cast_unknown_key_raises(vault_file):
    with pytest.raises(CastError, match="Key"):
        set_cast(vault_file, PASSWORD, "production", "MISSING", "int")


def test_set_cast_invalid_type_raises(vault_file):
    with pytest.raises(CastError, match="Unsupported type"):
        set_cast(vault_file, PASSWORD, "production", "PORT", "bytes")


# --- remove_cast ---

def test_remove_cast_returns_true(vault_file):
    set_cast(vault_file, PASSWORD, "production", "PORT", "int")
    assert remove_cast(vault_file, PASSWORD, "production", "PORT") is True


def test_remove_cast_not_found_returns_false(vault_file):
    assert remove_cast(vault_file, PASSWORD, "production", "PORT") is False


# --- list_casts ---

def test_list_casts_empty(vault_file):
    assert list_casts(vault_file, PASSWORD, "production") == {}


def test_list_casts_after_set(vault_file):
    set_cast(vault_file, PASSWORD, "production", "PORT", "int")
    set_cast(vault_file, PASSWORD, "production", "DEBUG", "bool")
    result = list_casts(vault_file, PASSWORD, "production")
    assert result == {"PORT": "int", "DEBUG": "bool"}


# --- apply_casts ---

def test_apply_casts_converts_values(vault_file):
    set_cast(vault_file, PASSWORD, "production", "PORT", "int")
    set_cast(vault_file, PASSWORD, "production", "DEBUG", "bool")
    set_cast(vault_file, PASSWORD, "production", "RATIO", "float")
    result = apply_casts(vault_file, PASSWORD, "production")
    assert result["PORT"] == 8080
    assert result["DEBUG"] is True
    assert result["RATIO"] == pytest.approx(3.14)


def test_apply_casts_uncasted_keys_remain_str(vault_file):
    set_cast(vault_file, PASSWORD, "production", "PORT", "int")
    result = apply_casts(vault_file, PASSWORD, "production")
    assert isinstance(result["DEBUG"], str)


def test_apply_casts_unknown_profile_raises(vault_file):
    with pytest.raises(CastError, match="Profile"):
        apply_casts(vault_file, PASSWORD, "nonexistent")
