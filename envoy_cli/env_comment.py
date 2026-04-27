"""Inline comment annotations for env keys."""

from __future__ import annotations

from envoy_cli.vault import load_vault, save_vault


class CommentError(Exception):
    pass


def _comments_store(vault: dict) -> dict:
    return vault.setdefault("__comments__", {})


def get_comment(vault_path: str, password: str, profile: str, key: str) -> str | None:
    """Return the inline comment for a key, or None if not set."""
    vault = load_vault(vault_path, password)
    profiles = vault.get("profiles", {})
    if profile not in profiles:
        raise CommentError(f"Profile '{profile}' not found.")
    if key not in profiles[profile]:
        raise CommentError(f"Key '{key}' not found in profile '{profile}'.")
    return _comments_store(vault).get(profile, {}).get(key)


def set_comment(vault_path: str, password: str, profile: str, key: str, text: str) -> str:
    """Set an inline comment for a key. Returns the comment text."""
    vault = load_vault(vault_path, password)
    profiles = vault.get("profiles", {})
    if profile not in profiles:
        raise CommentError(f"Profile '{profile}' not found.")
    if key not in profiles[profile]:
        raise CommentError(f"Key '{key}' not found in profile '{profile}'.")
    store = _comments_store(vault)
    store.setdefault(profile, {})[key] = text
    save_vault(vault_path, password, vault)
    return text


def remove_comment(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Remove the inline comment for a key. Returns True if removed, False if absent."""
    vault = load_vault(vault_path, password)
    store = _comments_store(vault)
    removed = store.get(profile, {}).pop(key, None) is not None
    if removed:
        save_vault(vault_path, password, vault)
    return removed


def list_comments(vault_path: str, password: str, profile: str) -> dict[str, str]:
    """Return all key->comment mappings for a profile."""
    vault = load_vault(vault_path, password)
    if profile not in vault.get("profiles", {}):
        raise CommentError(f"Profile '{profile}' not found.")
    return dict(_comments_store(vault).get(profile, {}))
