"""Attach freeform notes to profiles or individual keys in the vault."""

from __future__ import annotations

from envoy_cli.vault import load_vault, save_vault


class NoteError(Exception):
    pass


def _notes_store(vault: dict) -> dict:
    return vault.setdefault("__notes__", {})


def get_profile_note(vault_path: str, password: str, profile: str) -> str | None:
    """Return the note attached to a profile, or None."""
    vault = load_vault(vault_path, password)
    return _notes_store(vault).get(f"profile:{profile}")


def set_profile_note(vault_path: str, password: str, profile: str, text: str) -> str:
    """Attach a note to a profile. Returns the saved text."""
    vault = load_vault(vault_path, password)
    if profile not in vault.get("profiles", {}):
        raise NoteError(f"Profile '{profile}' not found.")
    _notes_store(vault)[f"profile:{profile}"] = text
    save_vault(vault_path, password, vault)
    return text


def remove_profile_note(vault_path: str, password: str, profile: str) -> bool:
    """Remove the note from a profile. Returns True if a note existed."""
    vault = load_vault(vault_path, password)
    key = f"profile:{profile}"
    store = _notes_store(vault)
    if key not in store:
        return False
    del store[key]
    save_vault(vault_path, password, vault)
    return True


def get_key_note(vault_path: str, password: str, profile: str, env_key: str) -> str | None:
    """Return the note attached to a specific key within a profile, or None."""
    vault = load_vault(vault_path, password)
    return _notes_store(vault).get(f"key:{profile}:{env_key}")


def set_key_note(vault_path: str, password: str, profile: str, env_key: str, text: str) -> str:
    """Attach a note to a specific key. Returns the saved text."""
    vault = load_vault(vault_path, password)
    profiles = vault.get("profiles", {})
    if profile not in profiles:
        raise NoteError(f"Profile '{profile}' not found.")
    if env_key not in profiles[profile]:
        raise NoteError(f"Key '{env_key}' not found in profile '{profile}'.")
    _notes_store(vault)[f"key:{profile}:{env_key}"] = text
    save_vault(vault_path, password, vault)
    return text


def remove_key_note(vault_path: str, password: str, profile: str, env_key: str) -> bool:
    """Remove a note from a specific key. Returns True if a note existed."""
    vault = load_vault(vault_path, password)
    store = _notes_store(vault)
    key = f"key:{profile}:{env_key}"
    if key not in store:
        return False
    del store[key]
    save_vault(vault_path, password, vault)
    return True


def list_notes(vault_path: str, password: str, profile: str) -> dict[str, str]:
    """Return all notes (profile-level and key-level) for a given profile."""
    vault = load_vault(vault_path, password)
    store = _notes_store(vault)
    result: dict[str, str] = {}
    profile_key = f"profile:{profile}"
    if profile_key in store:
        result["__profile__"] = store[profile_key]
    prefix = f"key:{profile}:"
    for k, v in store.items():
        if k.startswith(prefix):
            env_key = k[len(prefix):]
            result[env_key] = v
    return result
