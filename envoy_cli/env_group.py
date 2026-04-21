"""Group-based key management: assign keys to named groups within a profile."""

from envoy_cli.vault import load_vault, save_vault


class GroupError(Exception):
    pass


def _groups_store(vault: dict) -> dict:
    return vault.setdefault("__groups__", {})


def get_groups(vault: dict, profile: str) -> dict:
    """Return {group_name: [key, ...]} for the given profile."""
    return _groups_store(vault).get(profile, {})


def add_key_to_group(vault_path: str, password: str, profile: str, group: str, key: str) -> list:
    """Add *key* to *group* in *profile*. Returns sorted key list for the group."""
    vault = load_vault(vault_path, password)
    if profile not in vault:
        raise GroupError(f"Profile '{profile}' not found.")
    if key not in vault[profile]:
        raise GroupError(f"Key '{key}' not found in profile '{profile}'.")
    groups = _groups_store(vault).setdefault(profile, {})
    keys = groups.setdefault(group, [])
    if key not in keys:
        keys.append(key)
        keys.sort()
    save_vault(vault_path, password, vault)
    return keys


def remove_key_from_group(vault_path: str, password: str, profile: str, group: str, key: str) -> list:
    """Remove *key* from *group*. Returns remaining keys."""
    vault = load_vault(vault_path, password)
    groups = _groups_store(vault).get(profile, {})
    keys = groups.get(group, [])
    if key not in keys:
        raise GroupError(f"Key '{key}' is not in group '{group}'.")
    keys.remove(key)
    if not keys:
        groups.pop(group, None)
    save_vault(vault_path, password, vault)
    return keys


def list_groups(vault_path: str, password: str, profile: str) -> dict:
    """Return all groups and their keys for *profile*."""
    vault = load_vault(vault_path, password)
    return get_groups(vault, profile)


def get_keys_in_group(vault_path: str, password: str, profile: str, group: str) -> list:
    """Return keys belonging to *group* in *profile*."""
    vault = load_vault(vault_path, password)
    return get_groups(vault, profile).get(group, [])


def delete_group(vault_path: str, password: str, profile: str, group: str) -> None:
    """Delete an entire group (keys themselves are preserved in the profile)."""
    vault = load_vault(vault_path, password)
    groups = _groups_store(vault).get(profile, {})
    if group not in groups:
        raise GroupError(f"Group '{group}' not found in profile '{profile}'.")
    groups.pop(group)
    save_vault(vault_path, password, vault)
