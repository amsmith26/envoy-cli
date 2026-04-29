"""Placeholder management: mark keys as placeholders (not yet set)."""

from __future__ import annotations

from typing import List

from envoy_cli.vault import load_vault, save_vault


class PlaceholderError(Exception):
    pass


def _placeholders_store(vault: dict, profile: str) -> dict:
    return vault.setdefault("__placeholders__", {}).setdefault(profile, {})


def get_placeholder_keys(vault_path: str, password: str, profile: str) -> List[str]:
    """Return sorted list of keys marked as placeholders for *profile*."""
    vault = load_vault(vault_path, password)
    store = _placeholders_store(vault, profile)
    return sorted(store.keys())


def mark_placeholder(vault_path: str, password: str, profile: str, key: str, description: str = "") -> List[str]:
    """Mark *key* in *profile* as a placeholder. Returns updated sorted list."""
    vault = load_vault(vault_path, password)
    if profile not in vault.get("profiles", {}):
        raise PlaceholderError(f"Profile '{profile}' not found.")
    if key not in vault["profiles"][profile]:
        raise PlaceholderError(f"Key '{key}' not found in profile '{profile}'.")
    _placeholders_store(vault, profile)[key] = description.strip()
    save_vault(vault_path, password, vault)
    return sorted(_placeholders_store(vault, profile).keys())


def unmark_placeholder(vault_path: str, password: str, profile: str, key: str) -> List[str]:
    """Remove placeholder mark from *key*. Returns updated sorted list."""
    vault = load_vault(vault_path, password)
    store = _placeholders_store(vault, profile)
    if key not in store:
        raise PlaceholderError(f"Key '{key}' is not marked as a placeholder in '{profile}'.")
    del store[key]
    save_vault(vault_path, password, vault)
    return sorted(store.keys())


def get_placeholder_description(vault_path: str, password: str, profile: str, key: str) -> str | None:
    """Return description for a placeholder key, or None if not marked."""
    vault = load_vault(vault_path, password)
    store = _placeholders_store(vault, profile)
    return store.get(key)


def list_unset_placeholders(vault_path: str, password: str, profile: str) -> List[str]:
    """Return keys that are marked as placeholders AND have empty/whitespace-only values."""
    vault = load_vault(vault_path, password)
    store = _placeholders_store(vault, profile)
    env = vault.get("profiles", {}).get(profile, {})
    return sorted(k for k in store if not env.get(k, "").strip())
