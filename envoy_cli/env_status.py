"""Track and report the status of keys across profiles (active, deprecated, expired, readonly, etc.)."""

from __future__ import annotations

from typing import Any

from envoy_cli.vault import load_vault, save_vault


class StatusError(Exception):
    pass


_STATUS_META_KEYS = (
    "__deprecated__",
    "__readonly__",
    "__sensitive__",
    "__required__",
    "__masks__",
    "__expiry__",
)


def get_key_status(vault_file: str, password: str, profile: str, key: str) -> dict[str, Any]:
    """Return a status dict for a single key in a profile."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise StatusError(f"Profile '{profile}' not found.")
    env = vault[profile]
    if key not in env:
        raise StatusError(f"Key '{key}' not found in profile '{profile}'.")

    deprecated_map = vault.get("__deprecated__", {}).get(profile, {})
    readonly_keys = vault.get("__readonly__", {}).get(profile, [])
    sensitive_keys = vault.get("__sensitive__", {}).get(profile, [])
    required_keys = vault.get("__required__", {}).get(profile, [])
    masked_keys = vault.get("__masks__", {}).get(profile, [])
    expiry_map = vault.get("__expiry__", {}).get(profile, {})

    return {
        "key": key,
        "profile": profile,
        "value": env[key],
        "deprecated": key in deprecated_map,
        "deprecation_note": deprecated_map.get(key, {}).get("note") if key in deprecated_map else None,
        "readonly": key in readonly_keys,
        "sensitive": key in sensitive_keys,
        "required": key in required_keys,
        "masked": key in masked_keys,
        "expires_at": expiry_map.get(key),
    }


def get_profile_status(vault_file: str, password: str, profile: str) -> list[dict[str, Any]]:
    """Return status dicts for all keys in a profile."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise StatusError(f"Profile '{profile}' not found.")
    env = vault[profile]
    return [
        get_key_status(vault_file, password, profile, key)
        for key in sorted(env.keys())
        if not key.startswith("__")
    ]


def summarize_profile_status(vault_file: str, password: str, profile: str) -> dict[str, int]:
    """Return counts of keys by status flag."""
    statuses = get_profile_status(vault_file, password, profile)
    return {
        "total": len(statuses),
        "deprecated": sum(1 for s in statuses if s["deprecated"]),
        "readonly": sum(1 for s in statuses if s["readonly"]),
        "sensitive": sum(1 for s in statuses if s["sensitive"]),
        "required": sum(1 for s in statuses if s["required"]),
        "masked": sum(1 for s in statuses if s["masked"]),
        "expiring": sum(1 for s in statuses if s["expires_at"]),
    }
