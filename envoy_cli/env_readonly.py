"""Read-only key protection for env profiles."""
from __future__ import annotations

from typing import List

from envoy_cli.vault import load_vault, save_vault


class ReadonlyError(Exception):
    pass


def _readonly_store(vault: dict, profile: str) -> dict:
    meta = vault.setdefault("_meta", {})
    return meta.setdefault(f"{profile}.__readonly__", {})


def get_readonly_keys(vault_path: str, password: str, profile: str) -> List[str]:
    """Return sorted list of read-only keys for *profile*."""
    vault = load_vault(vault_path, password)
    store = _readonly_store(vault, profile)
    return sorted(store.get("keys", []))


def mark_readonly(vault_path: str, password: str, profile: str, key: str) -> List[str]:
    """Mark *key* in *profile* as read-only. Returns updated sorted list."""
    vault = load_vault(vault_path, password)
    if profile not in vault.get("profiles", {}):
        raise ReadonlyError(f"Profile '{profile}' not found.")
    if key not in vault["profiles"][profile]:
        raise ReadonlyError(f"Key '{key}' not found in profile '{profile}'.")
    store = _readonly_store(vault, profile)
    keys: List[str] = store.get("keys", [])
    if key not in keys:
        keys.append(key)
    store["keys"] = sorted(keys)
    save_vault(vault_path, password, vault)
    return store["keys"]


def unmark_readonly(vault_path: str, password: str, profile: str, key: str) -> List[str]:
    """Remove read-only protection from *key* in *profile*."""
    vault = load_vault(vault_path, password)
    store = _readonly_store(vault, profile)
    keys: List[str] = store.get("keys", [])
    if key not in keys:
        raise ReadonlyError(f"Key '{key}' is not marked read-only in profile '{profile}'.")
    keys.remove(key)
    store["keys"] = sorted(keys)
    save_vault(vault_path, password, vault)
    return store["keys"]


def is_readonly(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Return True if *key* in *profile* is read-only."""
    return key in get_readonly_keys(vault_path, password, profile)


def assert_not_readonly(vault_path: str, password: str, profile: str, key: str) -> None:
    """Raise ReadonlyError if *key* is protected."""
    if is_readonly(vault_path, password, profile, key):
        raise ReadonlyError(f"Key '{key}' is read-only in profile '{profile}' and cannot be modified.")
