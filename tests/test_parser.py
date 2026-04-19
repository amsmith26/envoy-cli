"""Tests for envoy_cli.parser module."""

import pytest
from envoy_cli.parser import parse_env_file, serialize_env, merge_env


SAMPLE_ENV = """
# Database config
DB_HOST=localhost
DB_PORT=5432
DB_NAME="my_database"
SECRET_KEY='supersecret'
EMPTY_VAL=
"""


def test_parse_basic():
    result = parse_env_file(SAMPLE_ENV)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_parse_strips_double_quotes():
    result = parse_env_file(SAMPLE_ENV)
    assert result["DB_NAME"] == "my_database"


def test_parse_strips_single_quotes():
    result = parse_env_file(SAMPLE_ENV)
    assert result["SECRET_KEY"] == "supersecret"


def test_parse_ignores_comments():
    result = parse_env_file(SAMPLE_ENV)
    assert not any(k.startswith("#") for k in result)


def test_parse_empty_value():
    result = parse_env_file(SAMPLE_ENV)
    assert result["EMPTY_VAL"] == ""


def test_serialize_roundtrip():
    original = {"FOO": "bar", "BAZ": "qux"}
    serialized = serialize_env(original)
    parsed = parse_env_file(serialized)
    assert parsed == original


def test_serialize_quotes_values_with_spaces():
    env = {"MSG": "hello world"}
    serialized = serialize_env(env)
    assert '"hello world"' in serialized


def test_merge_env_override():
    base = {"A": "1", "B": "2"}
    override = {"B": "99", "C": "3"}
    merged, changed = merge_env(base, override)
    assert merged["B"] == "99"
    assert merged["C"] == "3"
    assert merged["A"] == "1"
    assert "B" in changed
    assert "C" in changed


def test_merge_env_no_changes():
    base = {"A": "1"}
    _, changed = merge_env(base, {"A": "1"})
    assert changed == []
