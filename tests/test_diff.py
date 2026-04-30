"""Tests for envoy_cli.diff module."""

import pytest
from envoy_cli.diff import diff_envs, format_diff, has_changes


BASE = {"KEY1": "foo", "KEY2": "bar", "KEY3": "baz"}
TARGET = {"KEY1": "foo", "KEY2": "changed", "KEY4": "new"}


def test_diff_detects_added():
    result = diff_envs(BASE, TARGET)
    assert "KEY4" in result["added"]
    assert result["added"]["KEY4"] == ("", "new")


def test_diff_detects_removed():
    result = diff_envs(BASE, TARGET)
    assert "KEY3" in result["removed"]
    assert result["removed"]["KEY3"] == ("baz", "")


def test_diff_detects_changed():
    result = diff_envs(BASE, TARGET)
    assert "KEY2" in result["changed"]
    assert result["changed"]["KEY2"] == ("bar", "changed")


def test_diff_unchanged_key_not_present():
    result = diff_envs(BASE, TARGET)
    assert "KEY1" not in result["added"]
    assert "KEY1" not in result["removed"]
    assert "KEY1" not in result["changed"]


def test_diff_identical_envs():
    result = diff_envs(BASE, BASE)
    assert not has_changes(result)


def test_has_changes_true():
    result = diff_envs(BASE, TARGET)
    assert has_changes(result)


def test_format_diff_added_prefix():
    result = diff_envs({}, {"NEW": "val"})
    lines = format_diff(result)
    assert any(line.startswith("+") for line in lines)


def test_format_diff_removed_prefix():
    result = diff_envs({"OLD": "val"}, {})
    lines = format_diff(result)
    assert any(line.startswith("-") for line in lines)


def test_format_diff_changed_prefix():
    result = diff_envs({"K": "a"}, {"K": "b"})
    lines = format_diff(result)
    assert any(line.startswith("~") for line in lines)


def test_format_diff_empty():
    result = diff_envs(BASE, BASE)
    assert format_diff(result) == []


def test_format_diff_contains_key_and_values():
    """Ensure formatted lines include the key name and both old/new values."""
    result = diff_envs({"K": "old"}, {"K": "new"})
    lines = format_diff(result)
    changed_lines = [line for line in lines if line.startswith("~")]
    assert len(changed_lines) == 1
    assert "K" in changed_lines[0]
    assert "old" in changed_lines[0]
    assert "new" in changed_lines[0]
