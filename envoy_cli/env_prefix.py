"""Prefix filtering and stripping for environment profiles."""

from __future__ import annotations

from typing import Dict, List

from envoy_cli.vault import load_vault, save_vault


class PrefixError(Exception):
    pass


def _prefix_store(vault: dict) -> dict:
    return vault.setdefault("__prefixes__", {})


def get_prefix(vault: dict, profile: str) -> str | None:
    """Return the registered prefix for a profile, or None."""
    return _prefix_store(vault).get(profile)


def set_prefix(vault: dict, profile: str, prefix: str) -> str:
    """Register a prefix for a profile.

    Raises PrefixError if the profile does not exist.
    """
    if profile not in vault:
        raise PrefixError(f"Profile '{profile}' not found.")
    _prefix_store(vault)[profile] = prefix
    return prefix


def remove_prefix(vault: dict, profile: str) -> None:
    """Remove the prefix registration for a profile."""
    _prefix_store(vault).pop(profile, None)


def filter_by_prefix(
    vault: dict, profile: str, prefix: str, *, case_sensitive: bool = True
) -> Dict[str, str]:
    """Return only the keys in *profile* that start with *prefix*."""
    if profile not in vault:
        raise PrefixError(f"Profile '{profile}' not found.")
    env: dict = vault[profile]
    if not case_sensitive:
        prefix_cmp = prefix.lower()
        return {k: v for k, v in env.items() if k.lower().startswith(prefix_cmp)}
    return {k: v for k, v in env.items() if k.startswith(prefix)}


def strip_prefix(
    vault: dict, profile: str, prefix: str, *, case_sensitive: bool = True
) -> Dict[str, str]:
    """Return env dict with *prefix* removed from matching key names."""
    filtered = filter_by_prefix(vault, profile, prefix, case_sensitive=case_sensitive)
    if case_sensitive:
        return {k[len(prefix):]: v for k, v in filtered.items()}
    return {k[len(prefix):]: v for k, v in filtered.items()}


def list_prefixed_profiles(vault: dict) -> List[str]:
    """Return sorted list of profiles that have a registered prefix."""
    return sorted(_prefix_store(vault).keys())
