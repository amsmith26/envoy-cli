"""Archive and unarchive profiles within a vault."""

from __future__ import annotations

from typing import Dict, List

from envoy_cli.vault import load_vault, save_vault

_ARCHIVE_KEY = "__archived_profiles__"


class ArchiveError(Exception):
    pass


def _archive_store(vault: dict) -> dict:
    return vault.setdefault(_ARCHIVE_KEY, {})


def list_archived(vault_file: str, password: str) -> List[str]:
    """Return sorted list of archived profile names."""
    vault = load_vault(vault_file, password)
    return sorted(_archive_store(vault).keys())


def archive_profile(vault_file: str, password: str, profile: str) -> List[str]:
    """Move a profile into the archive store."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise ArchiveError(f"Profile '{profile}' not found.")
    if profile == _ARCHIVE_KEY:
        raise ArchiveError("Cannot archive internal metadata.")
    store = _archive_store(vault)
    if profile in store:
        raise ArchiveError(f"Profile '{profile}' is already archived.")
    store[profile] = vault.pop(profile)
    save_vault(vault_file, password, vault)
    return sorted(store.keys())


def unarchive_profile(vault_file: str, password: str, profile: str) -> List[str]:
    """Restore a profile from the archive back to active profiles."""
    vault = load_vault(vault_file, password)
    store = _archive_store(vault)
    if profile not in store:
        raise ArchiveError(f"Archived profile '{profile}' not found.")
    if profile in vault:
        raise ArchiveError(
            f"Profile '{profile}' already exists as an active profile."
        )
    vault[profile] = store.pop(profile)
    save_vault(vault_file, password, vault)
    return sorted(store.keys())


def get_archived_env(vault_file: str, password: str, profile: str) -> Dict[str, str]:
    """Return the env dict for an archived profile without restoring it."""
    vault = load_vault(vault_file, password)
    store = _archive_store(vault)
    if profile not in store:
        raise ArchiveError(f"Archived profile '{profile}' not found.")
    return dict(store[profile])
