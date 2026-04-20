"""Track per-profile value change history for env keys."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from envoy_cli.vault import load_vault, save_vault

_HISTORY_KEY = "__history__"
_MAX_ENTRIES = 50


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _history_store(vault: dict) -> dict:
    """Return the top-level history store, creating it if absent."""
    if _HISTORY_KEY not in vault:
        vault[_HISTORY_KEY] = {}
    return vault[_HISTORY_KEY]


def record_change(
    vault_file: str,
    password: str,
    profile: str,
    key: str,
    old_value: str | None,
    new_value: str | None,
) -> None:
    """Append a change entry for *key* in *profile* to the vault history."""
    vault = load_vault(vault_file, password)
    store = _history_store(vault)
    profile_history: dict[str, list] = store.setdefault(profile, {})
    entries: list[dict[str, Any]] = profile_history.setdefault(key, [])

    entries.append(
        {
            "timestamp": _now(),
            "old": old_value,
            "new": new_value,
        }
    )

    # Keep only the most recent entries to cap vault size
    profile_history[key] = entries[-_MAX_ENTRIES:]
    save_vault(vault_file, password, vault)


def get_key_history(
    vault_file: str,
    password: str,
    profile: str,
    key: str,
) -> list[dict[str, Any]]:
    """Return the list of change entries for *key* in *profile* (oldest first)."""
    vault = load_vault(vault_file, password)
    store = _history_store(vault)
    return store.get(profile, {}).get(key, [])


def get_profile_history(
    vault_file: str,
    password: str,
    profile: str,
) -> dict[str, list[dict[str, Any]]]:
    """Return all tracked key histories for *profile*."""
    vault = load_vault(vault_file, password)
    store = _history_store(vault)
    return store.get(profile, {})


def clear_history(
    vault_file: str,
    password: str,
    profile: str,
    key: str | None = None,
) -> None:
    """Clear history for *profile*. If *key* is given, clear only that key."""
    vault = load_vault(vault_file, password)
    store = _history_store(vault)
    if profile not in store:
        return
    if key is None:
        del store[profile]
    else:
        store[profile].pop(key, None)
    save_vault(vault_file, password, vault)
