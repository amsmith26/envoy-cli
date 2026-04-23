"""Expiry / TTL tracking for environment variable keys."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from envoy_cli.vault import load_vault, save_vault

_EXPIRY_STORE = "__expiry__"
_DT_FMT = "%Y-%m-%dT%H:%M:%SZ"


class ExpireError(Exception):
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _expiry_store(vault: dict, profile: str) -> dict:
    vault.setdefault(_EXPIRY_STORE, {}).setdefault(profile, {})
    return vault[_EXPIRY_STORE][profile]


def set_expiry(vault_path: str, password: str, profile: str, key: str, expires_at: datetime) -> str:
    """Set an expiry datetime (UTC) for a key in a profile."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise ExpireError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise ExpireError(f"Key '{key}' not found in profile '{profile}'.")
    _expiry_store(vault, profile)[key] = expires_at.strftime(_DT_FMT)
    save_vault(vault_path, password, vault)
    return expires_at.strftime(_DT_FMT)


def get_expiry(vault_path: str, password: str, profile: str, key: str) -> Optional[datetime]:
    """Return the expiry datetime for a key, or None if not set."""
    vault = load_vault(vault_path, password)
    store = vault.get(_EXPIRY_STORE, {}).get(profile, {})
    raw = store.get(key)
    if raw is None:
        return None
    return datetime.strptime(raw, _DT_FMT).replace(tzinfo=timezone.utc)


def remove_expiry(vault_path: str, password: str, profile: str, key: str) -> bool:
    """Remove the expiry for a key. Returns True if removed, False if not set."""
    vault = load_vault(vault_path, password)
    store = vault.get(_EXPIRY_STORE, {}).get(profile, {})
    if key not in store:
        return False
    del store[key]
    save_vault(vault_path, password, vault)
    return True


def list_expired(vault_path: str, password: str, profile: str) -> list[str]:
    """Return keys whose expiry has passed."""
    vault = load_vault(vault_path, password)
    store = vault.get(_EXPIRY_STORE, {}).get(profile, {})
    now = _utcnow()
    expired = []
    for key, raw in store.items():
        dt = datetime.strptime(raw, _DT_FMT).replace(tzinfo=timezone.utc)
        if dt <= now:
            expired.append(key)
    return sorted(expired)


def list_all_expiries(vault_path: str, password: str, profile: str) -> dict[str, str]:
    """Return a mapping of key -> ISO expiry string for all tracked keys."""
    vault = load_vault(vault_path, password)
    return dict(vault.get(_EXPIRY_STORE, {}).get(profile, {}))
