"""Rename keys across one or more profiles in the vault."""

from envoy_cli.vault import load_vault, save_vault, vault_exists


class RenameError(Exception):
    pass


def rename_key(vault_path: str, password: str, profile: str, old_key: str, new_key: str) -> bool:
    """
    Rename a key within a single profile.
    Returns True if the key was found and renamed, False if old_key not present.
    """
    if not vault_exists(vault_path):
        raise RenameError(f"Vault not found: {vault_path}")

    data = load_vault(vault_path, password)

    if profile not in data:
        raise RenameError(f"Profile '{profile}' does not exist.")

    env = data[profile]
    if old_key not in env:
        return False

    if new_key in env:
        raise RenameError(f"Key '{new_key}' already exists in profile '{profile}'.")

    env[new_key] = env.pop(old_key)
    data[profile] = env
    save_vault(vault_path, password, data)
    return True


def rename_key_all_profiles(vault_path: str, password: str, old_key: str, new_key: str) -> dict:
    """
    Rename a key across all profiles.
    Returns a dict mapping profile_name -> bool (True if renamed, False if key absent).
    """
    if not vault_exists(vault_path):
        raise RenameError(f"Vault not found: {vault_path}")

    data = load_vault(vault_path, password)
    results = {}

    for profile, env in data.items():
        if not isinstance(env, dict):
            continue
        if old_key in env:
            if new_key in env:
                raise RenameError(
                    f"Key '{new_key}' already exists in profile '{profile}'. Aborting."
                )
            env[new_key] = env.pop(old_key)
            results[profile] = True
        else:
            results[profile] = False

    save_vault(vault_path, password, data)
    return results
