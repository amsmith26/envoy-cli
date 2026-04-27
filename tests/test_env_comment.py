"""Tests for envoy_cli.env_comment."""

import pytest

from envoy_cli.env_comment import CommentError, get_comment, list_comments, remove_comment, set_comment
from envoy_cli.vault import save_vault


PASSWORD = "test-pass"


@pytest.fixture()
def vault_file(tmp_path):
    path = str(tmp_path / "test.vault")
    vault = {
        "profiles": {
            "dev": {"API_KEY": "abc123", "DEBUG": "true"},
            "prod": {"API_KEY": "xyz789"},
        }
    }
    save_vault(path, PASSWORD, vault)
    return path


def test_set_comment_returns_text(vault_file):
    result = set_comment(vault_file, PASSWORD, "dev", "API_KEY", "The API key")
    assert result == "The API key"


def test_get_comment_after_set(vault_file):
    set_comment(vault_file, PASSWORD, "dev", "API_KEY", "The API key")
    result = get_comment(vault_file, PASSWORD, "dev", "API_KEY")
    assert result == "The API key"


def test_get_comment_missing_returns_none(vault_file):
    result = get_comment(vault_file, PASSWORD, "dev", "DEBUG")
    assert result is None


def test_set_comment_unknown_profile_raises(vault_file):
    with pytest.raises(CommentError, match="Profile"):
        set_comment(vault_file, PASSWORD, "staging", "API_KEY", "text")


def test_set_comment_unknown_key_raises(vault_file):
    with pytest.raises(CommentError, match="Key"):
        set_comment(vault_file, PASSWORD, "dev", "NONEXISTENT", "text")


def test_get_comment_unknown_profile_raises(vault_file):
    with pytest.raises(CommentError, match="Profile"):
        get_comment(vault_file, PASSWORD, "ghost", "API_KEY")


def test_get_comment_unknown_key_raises(vault_file):
    with pytest.raises(CommentError, match="Key"):
        get_comment(vault_file, PASSWORD, "dev", "MISSING")


def test_remove_comment_returns_true_when_present(vault_file):
    set_comment(vault_file, PASSWORD, "dev", "API_KEY", "to remove")
    result = remove_comment(vault_file, PASSWORD, "dev", "API_KEY")
    assert result is True


def test_remove_comment_returns_false_when_absent(vault_file):
    result = remove_comment(vault_file, PASSWORD, "dev", "DEBUG")
    assert result is False


def test_remove_comment_clears_value(vault_file):
    set_comment(vault_file, PASSWORD, "dev", "API_KEY", "will be gone")
    remove_comment(vault_file, PASSWORD, "dev", "API_KEY")
    assert get_comment(vault_file, PASSWORD, "dev", "API_KEY") is None


def test_list_comments_empty(vault_file):
    result = list_comments(vault_file, PASSWORD, "dev")
    assert result == {}


def test_list_comments_after_set(vault_file):
    set_comment(vault_file, PASSWORD, "dev", "API_KEY", "key comment")
    set_comment(vault_file, PASSWORD, "dev", "DEBUG", "debug flag")
    result = list_comments(vault_file, PASSWORD, "dev")
    assert result == {"API_KEY": "key comment", "DEBUG": "debug flag"}


def test_list_comments_unknown_profile_raises(vault_file):
    with pytest.raises(CommentError, match="Profile"):
        list_comments(vault_file, PASSWORD, "nowhere")


def test_comments_isolated_per_profile(vault_file):
    set_comment(vault_file, PASSWORD, "dev", "API_KEY", "dev comment")
    result = list_comments(vault_file, PASSWORD, "prod")
    assert "API_KEY" not in result
