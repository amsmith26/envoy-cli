"""Mark keys as required in a profile and validate their presence."""

from __future__ import annotations

from typing import List

from envoy_cli.vault import load_vault, save_vault


class RequiredError(Exception):
    pass


def _required_store(vault: dict, profile: str) -> dict:
    return vault.setdefault("_required", {}).setdefault(profile, {})


def get_required_keys(vault_path: str, password: str, profile: str) -> List[str]:
    """Return list of keys marked as required for the profile."""
    vault = load_vault(vault_path, password)
    store = vault.get("_required", {}).get(profile, {})
    return sorted(store.get("keys", []))


def mark_required(vault_path: str, password: str, profile: str, key: str) -> List[str]:
    """Mark a key as required. Raises RequiredError if key not in profile."""
    vault = load_vault(vault_path, password)
    if profile not in vault.get("profiles", {}):
        raise RequiredError(f"Profile '{profile}' does not exist.")
    if key not in vault["profiles"][profile]:
        raise RequiredError(f"Key '{key}' not found in profile '{profile}'.")
    store = _required_store(vault, profile)
    keys = store.get("keys", [])
    if key not in keys:
        keys.append(key)
    store["keys"] = sorted(keys)
    save_vault(vault_path, password, vault)
    return store["keys"]


def unmark_required(vault_path: str, password: str, profile: str, key: str) -> List[str]:
    """Remove required mark from a key. Returns updated list."""
    vault = load_vault(vault_path, password)
    store = _required_store(vault, profile)
    keys = store.get("keys", [])
    if key not in keys:
        raise RequiredError(f"Key '{key}' is not marked as required in profile '{profile}'.")
    keys.remove(key)
    store["keys"] = sorted(keys)
    save_vault(vault_path, password, vault)
    return store["keys"]


def check_required(vault_path: str, password: str, profile: str) -> List[str]:
    """Return list of required keys that are missing or empty in the profile."""
    vault = load_vault(vault_path, password)
    store = vault.get("_required", {}).get(profile, {})
    required_keys = store.get("keys", [])
    env = vault.get("profiles", {}).get(profile, {})
    return [k for k in required_keys if not env.get(k, "").strip()]


def assert_required(vault_path: str, password: str, profile: str) -> None:
    """Raise RequiredError if any required keys are missing or empty in the profile.

    This is a convenience wrapper around check_required intended for use in
    activation flows where a hard failure is desired instead of a return value.
    """
    missing = check_required(vault_path, password, profile)
    if missing:
        keys_str = ", ".join(missing)
        raise RequiredError(
            f"Profile '{profile}' is missing required key(s): {keys_str}"
        )
