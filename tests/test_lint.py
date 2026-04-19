"""Tests for envoy_cli.lint module."""

import pytest
from envoy_cli.lint import lint_env, format_lint_results, _check_duplicate_keys, _check_unquoted_special_chars


def test_no_issues_clean_env():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    issues = lint_env(env)
    assert issues == []


def test_empty_value_detected():
    env = {"APP_NAME": "", "PORT": "8080"}
    issues = lint_env(env)
    assert any(i["rule"] == "empty_value" and i["key"] == "APP_NAME" for i in issues)


def test_invalid_key_lowercase():
    env = {"app_name": "myapp"}
    issues = lint_env(env)
    assert any(i["rule"] == "invalid_key" and i["key"] == "app_name" for i in issues)


def test_invalid_key_starts_with_digit():
    env = {"1BAD": "value"}
    issues = lint_env(env)
    assert any(i["rule"] == "invalid_key" for i in issues)


def test_valid_key_with_digits():
    env = {"APP2_NAME": "ok"}
    issues = lint_env(env)
    assert not any(i["rule"] == "invalid_key" for i in issues)


def test_duplicate_key_detected():
    raw_lines = ["APP=foo", "PORT=8080", "APP=bar"]
    issues = _check_duplicate_keys(raw_lines)
    assert any(i["rule"] == "duplicate_key" and i["key"] == "APP" for i in issues)


def test_no_duplicate_keys():
    raw_lines = ["APP=foo", "PORT=8080"]
    issues = _check_duplicate_keys(raw_lines)
    assert issues == []


def test_duplicate_key_skips_comments():
    raw_lines = ["# APP=foo", "APP=bar"]
    issues = _check_duplicate_keys(raw_lines)
    assert issues == []


def test_unquoted_special_chars_space():
    raw_lines = ["GREETING=hello world"]
    issues = _check_unquoted_special_chars(raw_lines)
    assert any(i["rule"] == "unquoted_special_chars" and i["key"] == "GREETING" for i in issues)


def test_quoted_special_chars_ok():
    raw_lines = ['GREETING="hello world"']
    issues = _check_unquoted_special_chars(raw_lines)
    assert issues == []


def test_format_no_issues():
    result = format_lint_results([])
    assert result == "No issues found."


def test_format_with_issues():
    issues = [{"rule": "empty_value", "key": "X", "message": "'X' has an empty value"}]
    result = format_lint_results(issues)
    assert "empty_value" in result
    assert "'X'" in result


def test_lint_env_with_raw_lines():
    env = {"APP": "foo", "APP": "bar"}  # noqa: F601 — dict deduplicates, use raw_lines
    raw_lines = ["APP=foo", "APP=bar"]
    issues = lint_env(env, raw_lines)
    assert any(i["rule"] == "duplicate_key" for i in issues)
