"""Boolean flag management for env keys within a profile."""

from __future__ import annotations

from typing import List

from envoy_cli.vault import load_vault, save_vault

_FLAGS_KEY = "__flags__"


class FlagError(Exception):
    pass


def _flags_store(vault: dict) -> dict:
    return vault.setdefault(_FLAGS_KEY, {})


def get_flags(vault_path: str, password: str, profile: str) -> dict:
    """Return a dict of {key: bool} flags for the given profile."""
    vault = load_vault(vault_path, password)
    return dict(_flags_store(vault).get(profile, {}))


def set_flag(vault_path: str, password: str, profile: str, key: str, value: bool) -> bool:
    """Set a boolean flag on a key. Returns the new flag value."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise FlagError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise FlagError(f"Key '{key}' not found in profile '{profile}'.")
    _flags_store(vault).setdefault(profile, {})[key] = bool(value)
    save_vault(vault_path, password, vault)
    return bool(value)


def remove_flag(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Remove a flag from a key. Returns True if removed, False if not present."""
    vault = load_vault(vault_path, password)
    store = _flags_store(vault).get(profile, {})
    if key not in store:
        return False
    del store[key]
    _flags_store(vault)[profile] = store
    save_vault(vault_path, password, vault)
    return True


def list_flagged_keys(vault_path: str, password: str, profile: str, value: bool | None = None) -> List[str]:
    """List keys that have flags set. Optionally filter by flag value."""
    flags = get_flags(vault_path, password, profile)
    if value is None:
        return sorted(flags.keys())
    return sorted(k for k, v in flags.items() if v == value)
