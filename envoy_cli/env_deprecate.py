"""Mark env keys as deprecated with optional replacement suggestions."""

from __future__ import annotations

from typing import Optional

from envoy_cli.vault import load_vault, save_vault


class DeprecateError(Exception):
    pass


def _deprecations_store(vault: dict, profile: str) -> dict:
    return vault.setdefault("_deprecations", {}).setdefault(profile, {})


def get_deprecations(vault_path: str, password: str, profile: str) -> dict:
    """Return all deprecated keys for a profile as {key: {reason, replacement}}."""
    vault = load_vault(vault_path, password)
    return dict(_deprecations_store(vault, profile))


def deprecate_key(
    vault_path: str,
    password: str,
    profile: str,
    key: str,
    reason: str = "",
    replacement: Optional[str] = None,
) -> dict:
    """Mark a key as deprecated. Returns the deprecation record."""
    vault = load_vault(vault_path, password)
    profiles = vault.get("profiles", {})
    if profile not in profiles:
        raise DeprecateError(f"Profile '{profile}' not found.")
    if key not in profiles[profile]:
        raise DeprecateError(f"Key '{key}' not found in profile '{profile}'.")
    record = {"reason": reason, "replacement": replacement}
    _deprecations_store(vault, profile)[key] = record
    save_vault(vault_path, password, vault)
    return record


def undeprecate_key(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Remove deprecation marker from a key. Returns True if removed, False if not found."""
    vault = load_vault(vault_path, password)
    store = _deprecations_store(vault, profile)
    if key not in store:
        return False
    del store[key]
    save_vault(vault_path, password, vault)
    return True


def is_deprecated(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Return True if the key is marked deprecated."""
    vault = load_vault(vault_path, password)
    return key in _deprecations_store(vault, profile)


def check_deprecated_usage(
    vault_path: str, password: str, profile: str
) -> list[dict]:
    """Return a list of violations: deprecated keys that still exist in the profile."""
    vault = load_vault(vault_path, password)
    profiles = vault.get("profiles", {})
    env = profiles.get(profile, {})
    store = _deprecations_store(vault, profile)
    violations = []
    for key, meta in store.items():
        if key in env:
            violations.append({"key": key, **meta})
    return violations
