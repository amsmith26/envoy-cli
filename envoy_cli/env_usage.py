"""Track access/usage statistics for env keys per profile."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from envoy_cli.vault import load_vault, save_vault

_USAGE_STORE = "__usage__"


class UsageError(Exception):
    pass


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _usage_store(vault: dict) -> dict:
    vault.setdefault(_USAGE_STORE, {})
    return vault[_USAGE_STORE]


def record_access(vault_file: str, password: str, profile: str, key: str) -> dict:
    """Record that a key was accessed. Returns the updated usage record."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise UsageError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise UsageError(f"Key '{key}' not found in profile '{profile}'.")
    store = _usage_store(vault)
    store.setdefault(profile, {})
    entry = store[profile].setdefault(key, {"count": 0, "first_access": None, "last_access": None})
    entry["count"] += 1
    now = _utcnow()
    if entry["first_access"] is None:
        entry["first_access"] = now
    entry["last_access"] = now
    save_vault(vault_file, password, vault)
    return dict(entry)


def get_usage(vault_file: str, password: str, profile: str, key: str) -> Optional[dict]:
    """Return usage stats for a key, or None if never accessed."""
    vault = load_vault(vault_file, password)
    store = _usage_store(vault)
    return store.get(profile, {}).get(key)


def get_profile_usage(vault_file: str, password: str, profile: str) -> Dict[str, dict]:
    """Return usage stats for all keys in a profile."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise UsageError(f"Profile '{profile}' not found.")
    store = _usage_store(vault)
    return dict(store.get(profile, {}))


def reset_usage(vault_file: str, password: str, profile: str, key: str) -> bool:
    """Reset usage stats for a specific key. Returns True if stats existed."""
    vault = load_vault(vault_file, password)
    store = _usage_store(vault)
    if key in store.get(profile, {}):
        del store[profile][key]
        if not store[profile]:
            del store[profile]
        save_vault(vault_file, password, vault)
        return True
    return False


def top_keys(vault_file: str, password: str, profile: str, n: int = 5) -> List[dict]:
    """Return the top-n most accessed keys in a profile."""
    usage = get_profile_usage(vault_file, password, profile)
    ranked = sorted(usage.items(), key=lambda x: x[1]["count"], reverse=True)
    return [{"key": k, **v} for k, v in ranked[:n]]
