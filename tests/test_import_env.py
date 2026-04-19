"""Tests for envoy_cli.import_env module."""
import os
import pytest
from envoy_cli.import_env import (
    import_from_shell,
    import_from_json,
    import_from_dotenv_string,
    import_env,
)


def test_import_from_shell_all(monkeypatch):
    monkeypatch.setenv("TEST_VAR_X", "hello")
    result = import_from_shell()
    assert "TEST_VAR_X" in result
    assert result["TEST_VAR_X"] == "hello"


def test_import_from_shell_filtered(monkeypatch):
    monkeypatch.setenv("KEEP_ME", "yes")
    monkeypatch.setenv("SKIP_ME", "no")
    result = import_from_shell(keys=["KEEP_ME"])
    assert "KEEP_ME" in result
    assert "SKIP_ME" not in result


def test_import_from_shell_missing_key(monkeypatch):
    result = import_from_shell(keys=["DEFINITELY_NOT_SET_XYZ"])
    assert result == {}


def test_import_from_json_basic():
    result = import_from_json('{"FOO": "bar", "NUM": "42"}')
    assert result == {"FOO": "bar", "NUM": "42"}


def test_import_from_json_invalid():
    with pytest.raises(ValueError, match="Invalid JSON"):
        import_from_json("not json")


def test_import_from_json_not_object():
    with pytest.raises(ValueError, match="JSON must be an object"):
        import_from_json('["a", "b"]')


def test_import_from_dotenv_string_basic():
    raw = "KEY=value\nANOTHER=thing\n"
    result = import_from_dotenv_string(raw)
    assert result == {"KEY": "value", "ANOTHER": "thing"}


def test_import_from_dotenv_string_strips_quotes():
    raw = 'QUOTED="hello world"\nSINGLE=\'test\'\n'
    result = import_from_dotenv_string(raw)
    assert result["QUOTED"] == "hello world"
    assert result["SINGLE"] == "test"


def test_import_from_dotenv_string_ignores_comments():
    raw = "# comment\nKEY=val\n"
    result = import_from_dotenv_string(raw)
    assert "# comment" not in result
    assert result == {"KEY": "val"}


def test_import_from_dotenv_string_empty_value():
    raw = "EMPTY=\n"
    result = import_from_dotenv_string(raw)
    assert result["EMPTY"] == ""


def test_import_env_dotenv_format():
    result = import_env("A=1\nB=2", fmt="dotenv")
    assert result == {"A": "1", "B": "2"}


def test_import_env_json_format():
    result = import_env('{"X": "10"}', fmt="json")
    assert result == {"X": "10"}


def test_import_env_shell_format(monkeypatch):
    monkeypatch.setenv("MY_SHELL_VAR", "present")
    result = import_env("", fmt="shell", keys=["MY_SHELL_VAR"])
    assert result["MY_SHELL_VAR"] == "present"


def test_import_env_unknown_format():
    with pytest.raises(ValueError, match="Unknown import format"):
        import_env("data", fmt="yaml")
