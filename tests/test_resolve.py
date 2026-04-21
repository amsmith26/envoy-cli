"""Tests for envoy_cli.resolve."""

import pytest
from envoy_cli.resolve import (
    find_references,
    resolve_env,
    list_unresolved,
    ResolveError,
)


def test_find_references_none():
    assert find_references("hello world") == []


def test_find_references_single():
    assert find_references("${FOO}") == ["FOO"]


def test_find_references_multiple():
    refs = find_references("${HOST}:${PORT}")
    assert refs == ["HOST", "PORT"]


def test_resolve_simple_reference():
    env = {"HOST": "localhost", "URL": "http://${HOST}/api"}
    result = resolve_env(env)
    assert result["URL"] == "http://localhost/api"


def test_resolve_chained_references():
    env = {
        "SCHEME": "https",
        "HOST": "example.com",
        "BASE": "${SCHEME}://${HOST}",
        "URL": "${BASE}/path",
    }
    result = resolve_env(env)
    assert result["URL"] == "https://example.com/path"


def test_resolve_no_references_unchanged():
    env = {"KEY": "value", "OTHER": "plain"}
    result = resolve_env(env)
    assert result == env


def test_resolve_strict_raises_on_undefined():
    env = {"URL": "http://${UNDEFINED_HOST}/"}
    with pytest.raises(ResolveError, match="undefined variable"):
        resolve_env(env, strict=True)


def test_resolve_lenient_leaves_undefined():
    env = {"URL": "http://${UNDEFINED_HOST}/"}
    result = resolve_env(env, strict=False)
    assert "${UNDEFINED_HOST}" in result["URL"]


def test_resolve_circular_raises():
    env = {"A": "${B}", "B": "${A}"}
    with pytest.raises(ResolveError, match="Circular"):
        resolve_env(env, strict=True)


def test_resolve_returns_new_dict():
    env = {"FOO": "bar"}
    result = resolve_env(env)
    assert result is not env


def test_list_unresolved_empty_when_all_resolved():
    env = {"HOST": "localhost", "URL": "http://${HOST}"}
    assert list_unresolved(env) == {}


def test_list_unresolved_detects_missing():
    env = {"URL": "http://${MISSING_HOST}/"}
    result = list_unresolved(env)
    assert "URL" in result
    assert "MISSING_HOST" in result["URL"]


def test_list_unresolved_multiple_keys():
    env = {
        "A": "${X}",
        "B": "${Y}",
        "X": "defined",
    }
    result = list_unresolved(env)
    assert "B" in result
    assert "A" not in result
