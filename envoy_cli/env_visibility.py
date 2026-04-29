"""Manage visibility levels for keys within a profile.

Supported levels: public, internal, private, secret
"""

from __future__ import annotations

from envoy_cli.vault import load_vault, save_vault

VISIBILITY_LEVELS = ("public", "internal", "private", "secret")


class VisibilityError(Exception):
    """Raised when a visibility operation fails."""


def _visibility_store(vault: dict) -> dict:
    return vault.setdefault("__visibility__", {})


def get_visibility(vault_file: str, password: str, profile: str, key: str) -> str | None:
    """Return the visibility level for *key* in *profile*, or None if unset."""
    vault = load_vault(vault_file, password)
    return _visibility_store(vault).get(profile, {}).get(key)


def set_visibility(
    vault_file: str, password: str, profile: str, key: str, level: str
) -> str:
    """Set the visibility *level* for *key* in *profile*. Returns the level."""
    if level not in VISIBILITY_LEVELS:
        raise VisibilityError(
            f"Invalid visibility level '{level}'. Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise VisibilityError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise VisibilityError(f"Key '{key}' not found in profile '{profile}'.")
    _visibility_store(vault).setdefault(profile, {})[key] = level
    save_vault(vault_file, password, vault)
    return level


def remove_visibility(vault_file: str, password: str, profile: str, key: str) -> bool:
    """Remove the visibility setting for *key* in *profile*. Returns True if removed."""
    vault = load_vault(vault_file, password)
    store = _visibility_store(vault)
    removed = store.get(profile, {}).pop(key, None) is not None
    if removed:
        save_vault(vault_file, password, vault)
    return removed


def list_visibility(vault_file: str, password: str, profile: str) -> dict[str, str]:
    """Return a mapping of key -> visibility level for *profile*."""
    vault = load_vault(vault_file, password)
    return dict(_visibility_store(vault).get(profile, {}))


def filter_by_visibility(
    vault_file: str, password: str, profile: str, level: str
) -> list[str]:
    """Return sorted list of keys in *profile* that have the given visibility *level*."""
    if level not in VISIBILITY_LEVELS:
        raise VisibilityError(
            f"Invalid visibility level '{level}'. Choose from: {', '.join(VISIBILITY_LEVELS)}"
        )
    vault = load_vault(vault_file, password)
    store = _visibility_store(vault).get(profile, {})
    return sorted(k for k, v in store.items() if v == level)
