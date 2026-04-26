"""Priority ordering for profiles — assign and query resolution priority."""

from __future__ import annotations

from typing import Dict, List

from envoy_cli.vault import load_vault, save_vault


class PriorityError(Exception):
    pass


_PRIORITY_KEY = "__priorities__"


def _priorities_store(vault: dict) -> Dict[str, int]:
    return vault.setdefault(_PRIORITY_KEY, {})


def get_priority(vault_path: str, password: str, profile: str) -> int | None:
    vault = load_vault(vault_path, password)
    return _priorities_store(vault).get(profile)


def set_priority(vault_path: str, password: str, profile: str, priority: int) -> int:
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise PriorityError(f"Profile '{profile}' does not exist.")
    if not isinstance(priority, int) or priority < 0:
        raise PriorityError("Priority must be a non-negative integer.")
    _priorities_store(vault)[profile] = priority
    save_vault(vault_path, password, vault)
    return priority


def remove_priority(vault_path: str, password: str, profile: str) -> bool:
    vault = load_vault(vault_path, password)
    store = _priorities_store(vault)
    if profile not in store:
        return False
    del store[profile]
    save_vault(vault_path, password, vault)
    return True


def list_priorities(vault_path: str, password: str) -> List[Dict[str, object]]:
    """Return profiles sorted by priority ascending (lower = higher priority)."""
    vault = load_vault(vault_path, password)
    store = _priorities_store(vault)
    entries = [
        {"profile": profile, "priority": prio}
        for profile, prio in store.items()
    ]
    return sorted(entries, key=lambda e: (e["priority"], e["profile"]))


def resolve_priority_order(vault_path: str, password: str) -> List[str]:
    """Return profile names ordered by priority; unranked profiles come last."""
    vault = load_vault(vault_path, password)
    store = _priorities_store(vault)
    ranked = sorted(
        ((prio, name) for name, prio in store.items()),
        key=lambda x: (x[0], x[1]),
    )
    ranked_names = [name for _, name in ranked]
    all_profiles = [k for k in vault if not k.startswith("__")]
    unranked = sorted(p for p in all_profiles if p not in store)
    return ranked_names + unranked
