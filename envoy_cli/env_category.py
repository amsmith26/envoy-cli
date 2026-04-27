"""Category management for grouping profiles by logical category."""

from __future__ import annotations

from typing import Dict, List, Optional

from envoy_cli.vault import load_vault, save_vault


class CategoryError(Exception):
    pass


def _categories_store(vault: dict) -> dict:
    return vault.setdefault("__categories__", {})


def get_category(vault_path: str, password: str, profile: str) -> Optional[str]:
    """Return the category assigned to a profile, or None."""
    vault = load_vault(vault_path, password)
    return _categories_store(vault).get(profile)


def set_category(vault_path: str, password: str, profile: str, category: str) -> str:
    """Assign a category to a profile. Returns the category name."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise CategoryError(f"Profile '{profile}' does not exist.")
    if not category or not category.strip():
        raise CategoryError("Category name must not be empty.")
    category = category.strip()
    _categories_store(vault)[profile] = category
    save_vault(vault_path, password, vault)
    return category


def remove_category(vault_path: str, password: str, profile: str) -> bool:
    """Remove the category from a profile. Returns True if removed, False if none set."""
    vault = load_vault(vault_path, password)
    store = _categories_store(vault)
    if profile not in store:
        return False
    del store[profile]
    save_vault(vault_path, password, vault)
    return True


def list_by_category(vault_path: str, password: str) -> Dict[str, List[str]]:
    """Return a dict mapping category -> sorted list of profiles in that category."""
    vault = load_vault(vault_path, password)
    store = _categories_store(vault)
    result: Dict[str, List[str]] = {}
    for profile, category in store.items():
        result.setdefault(category, []).append(profile)
    for cat in result:
        result[cat].sort()
    return result


def list_uncategorized(vault_path: str, password: str) -> List[str]:
    """Return sorted list of profiles that have no category assigned."""
    vault = load_vault(vault_path, password)
    store = _categories_store(vault)
    profiles = [p for p in vault if not p.startswith("__")]
    return sorted(p for p in profiles if p not in store)
