"""Tests for envoy_cli.env_note."""

import pytest

from envoy_cli.vault import save_vault
from envoy_cli.env_note import (
    NoteError,
    get_profile_note,
    set_profile_note,
    remove_profile_note,
    get_key_note,
    set_key_note,
    remove_key_note,
    list_notes,
)


@pytest.fixture
def vault_file(tmp_path):
    path = tmp_path / "test.vault"
    vault = {
        "profiles": {
            "production": {"API_KEY": "secret", "DEBUG": "false"},
            "staging": {"API_KEY": "staging-secret"},
        }
    }
    save_vault(str(path), "pass", vault)
    return str(path)


def test_set_profile_note_returns_text(vault_file):
    result = set_profile_note(vault_file, "pass", "production", "Live environment")
    assert result == "Live environment"


def test_get_profile_note_after_set(vault_file):
    set_profile_note(vault_file, "pass", "production", "Live environment")
    note = get_profile_note(vault_file, "pass", "production")
    assert note == "Live environment"


def test_get_profile_note_missing_returns_none(vault_file):
    note = get_profile_note(vault_file, "pass", "staging")
    assert note is None


def test_set_profile_note_unknown_profile_raises(vault_file):
    with pytest.raises(NoteError, match="Profile 'ghost' not found"):
        set_profile_note(vault_file, "pass", "ghost", "some note")


def test_remove_profile_note_returns_true(vault_file):
    set_profile_note(vault_file, "pass", "production", "to remove")
    assert remove_profile_note(vault_file, "pass", "production") is True


def test_remove_profile_note_absent_returns_false(vault_file):
    assert remove_profile_note(vault_file, "pass", "production") is False


def test_remove_profile_note_clears_note(vault_file):
    set_profile_note(vault_file, "pass", "production", "to remove")
    remove_profile_note(vault_file, "pass", "production")
    assert get_profile_note(vault_file, "pass", "production") is None


def test_set_key_note_returns_text(vault_file):
    result = set_key_note(vault_file, "pass", "production", "API_KEY", "The main API key")
    assert result == "The main API key"


def test_get_key_note_after_set(vault_file):
    set_key_note(vault_file, "pass", "production", "API_KEY", "The main API key")
    note = get_key_note(vault_file, "pass", "production", "API_KEY")
    assert note == "The main API key"


def test_get_key_note_missing_returns_none(vault_file):
    assert get_key_note(vault_file, "pass", "production", "DEBUG") is None


def test_set_key_note_unknown_profile_raises(vault_file):
    with pytest.raises(NoteError, match="Profile 'ghost' not found"):
        set_key_note(vault_file, "pass", "ghost", "API_KEY", "note")


def test_set_key_note_unknown_key_raises(vault_file):
    with pytest.raises(NoteError, match="Key 'MISSING' not found"):
        set_key_note(vault_file, "pass", "production", "MISSING", "note")


def test_remove_key_note_returns_true(vault_file):
    set_key_note(vault_file, "pass", "production", "API_KEY", "note")
    assert remove_key_note(vault_file, "pass", "production", "API_KEY") is True


def test_remove_key_note_absent_returns_false(vault_file):
    assert remove_key_note(vault_file, "pass", "production", "API_KEY") is False


def test_list_notes_includes_profile_and_key_notes(vault_file):
    set_profile_note(vault_file, "pass", "production", "Profile note")
    set_key_note(vault_file, "pass", "production", "API_KEY", "Key note")
    notes = list_notes(vault_file, "pass", "production")
    assert notes["__profile__"] == "Profile note"
    assert notes["API_KEY"] == "Key note"


def test_list_notes_excludes_other_profiles(vault_file):
    set_key_note(vault_file, "pass", "staging", "API_KEY", "Staging key note")
    notes = list_notes(vault_file, "pass", "production")
    assert "API_KEY" not in notes


def test_list_notes_empty_when_no_notes(vault_file):
    notes = list_notes(vault_file, "pass", "production")
    assert notes == {}
