"""Regex-based search and validation for env key values."""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

from envoy_cli.vault import load_vault, save_vault


class RegexError(Exception):
    """Raised when a regex operation fails."""


def _regex_store(vault: dict) -> dict:
    return vault.setdefault("__regex_patterns__", {})


def get_pattern(vault: dict, profile: str, key: str) -> str | None:
    """Return the stored regex pattern for a key, or None."""
    return _regex_store(vault).get(profile, {}).get(key)


def set_pattern(vault_file: str, password: str, profile: str, key: str, pattern: str) -> str:
    """Attach a regex validation pattern to a key. Returns the compiled pattern string."""
    try:
        re.compile(pattern)
    except re.error as exc:
        raise RegexError(f"Invalid regex pattern: {exc}") from exc

    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise RegexError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise RegexError(f"Key '{key}' not found in profile '{profile}'.")

    _regex_store(vault).setdefault(profile, {})[key] = pattern
    save_vault(vault_file, password, vault)
    return pattern


def remove_pattern(vault_file: str, password: str, profile: str, key: str) -> bool:
    """Remove the regex pattern for a key. Returns True if removed, False if not found."""
    vault = load_vault(vault_file, password)
    store = _regex_store(vault).get(profile, {})
    if key not in store:
        return False
    del store[key]
    save_vault(vault_file, password, vault)
    return True


def list_patterns(vault: dict, profile: str) -> Dict[str, str]:
    """Return all key→pattern mappings for a profile."""
    return dict(_regex_store(vault).get(profile, {}))


def validate_profile(vault: dict, profile: str) -> List[Tuple[str, str, str]]:
    """Validate all keys in a profile against their patterns.

    Returns a list of (key, value, pattern) tuples for violations.
    """
    violations: List[Tuple[str, str, str]] = []
    env = vault.get(profile, {})
    patterns = _regex_store(vault).get(profile, {})
    for key, pattern in patterns.items():
        value = env.get(key, "")
        if not re.fullmatch(pattern, value):
            violations.append((key, value, pattern))
    return violations
