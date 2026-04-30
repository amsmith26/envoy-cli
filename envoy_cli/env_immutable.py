"""Immutable key management: prevent keys from being modified or deleted."""

from __future__ import annotations

from typing import List

from envoy_cli.vault import load_vault, save_vault


class ImmutableError(Exception):
    pass


def _immutable_store(vault: dict, profile: str) -> dict:
    return vault.setdefault("_immutable", {}).setdefault(profile, {})


def get_immutable_keys(vault_path: str, password: str, profile: str) -> List[str]:
    """Return sorted list of immutable keys for a profile."""
    vault = load_vault(vault_path, password)
    store = vault.get("_immutable", {}).get(profile, {})
    return sorted(store.keys())


def mark_immutable(vault_path: str, password: str, profile: str, key: str) -> List[str]:
    """Mark a key as immutable. Raises ImmutableError if key does not exist."""
    vault = load_vault(vault_path, password)
    profiles = vault.get("profiles", {})
    if profile not in profiles:
        raise ImmutableError(f"Profile '{profile}' not found.")
    if key not in profiles[profile]:
        raise ImmutableError(f"Key '{key}' not found in profile '{profile}'.")
    store = _immutable_store(vault, profile)
    store[key] = True
    save_vault(vault_path, password, vault)
    return sorted(store.keys())


def unmark_immutable(vault_path: str, password: str, profile: str, key: str) -> List[str]:
    """Remove immutable flag from a key. Returns remaining immutable keys."""
    vault = load_vault(vault_path, password)
    store = _immutable_store(vault, profile)
    store.pop(key, None)
    save_vault(vault_path, password, vault)
    return sorted(store.keys())


def is_immutable(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Return True if the key is marked immutable."""
    vault = load_vault(vault_path, password)
    return vault.get("_immutable", {}).get(profile, {}).get(key, False)


def check_immutable(vault_path: str, password: str, profile: str, key: str) -> None:
    """Raise ImmutableError if the key is immutable."""
    if is_immutable(vault_path, password, profile, key):
        raise ImmutableError(
            f"Key '{key}' in profile '{profile}' is immutable and cannot be modified."
        )
