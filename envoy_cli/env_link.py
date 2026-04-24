"""Link a key in one profile to a key in another, so the value is always synced."""

from __future__ import annotations

from typing import Optional

from envoy_cli.vault import load_vault, save_vault


class LinkError(Exception):
    pass


def _links_store(vault: dict) -> dict:
    return vault.setdefault("__links__", {})


def get_links(vault_file: str, password: str) -> dict[str, dict]:
    """Return all links as {profile: {key: {src_profile, src_key}}}."""
    vault = load_vault(vault_file, password)
    return dict(_links_store(vault))


def add_link(
    vault_file: str,
    password: str,
    profile: str,
    key: str,
    src_profile: str,
    src_key: str,
) -> dict:
    """Link profile.key -> src_profile.src_key. Raises LinkError on conflicts."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise LinkError(f"Profile '{profile}' not found.")
    if src_profile not in vault:
        raise LinkError(f"Source profile '{src_profile}' not found.")
    if key not in vault[profile]:
        raise LinkError(f"Key '{key}' not found in profile '{profile}'.")
    if src_key not in vault[src_profile]:
        raise LinkError(f"Key '{src_key}' not found in profile '{src_profile}'.")

    store = _links_store(vault)
    profile_links = store.setdefault(profile, {})
    profile_links[key] = {"src_profile": src_profile, "src_key": src_key}

    save_vault(vault_file, password, vault)
    return profile_links[key]


def remove_link(vault_file: str, password: str, profile: str, key: str) -> bool:
    """Remove a link. Returns True if removed, False if it did not exist."""
    vault = load_vault(vault_file, password)
    store = _links_store(vault)
    removed = store.get(profile, {}).pop(key, None) is not None
    if removed:
        save_vault(vault_file, password, vault)
    return removed


def resolve_links(vault_file: str, password: str, profile: str) -> dict[str, str]:
    """Return the profile env with linked keys resolved from their sources."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise LinkError(f"Profile '{profile}' not found.")
    env = dict(vault[profile])
    store = _links_store(vault)
    for key, ref in store.get(profile, {}).items():
        src_profile = ref["src_profile"]
        src_key = ref["src_key"]
        if src_profile in vault and src_key in vault[src_profile]:
            env[key] = vault[src_profile][src_key]
    return env
