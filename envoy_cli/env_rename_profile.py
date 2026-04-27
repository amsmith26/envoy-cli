"""Rename a profile within the vault."""

from envoy_cli.vault import load_vault, save_vault


class RenameProfileError(Exception):
    pass


def rename_profile(vault_path: str, password: str, old_name: str, new_name: str) -> str:
    """Rename a profile from old_name to new_name.

    Returns the new profile name on success.
    Raises RenameProfileError if old_name does not exist or new_name already exists.
    """
    vault = load_vault(vault_path, password)

    if old_name not in vault:
        raise RenameProfileError(f"Profile '{old_name}' does not exist.")

    if new_name in vault:
        raise RenameProfileError(f"Profile '{new_name}' already exists.")

    if not new_name or not new_name.strip():
        raise RenameProfileError("New profile name must not be empty.")

    vault[new_name] = vault.pop(old_name)
    save_vault(vault_path, password, vault)
    return new_name


def list_profile_names(vault_path: str, password: str) -> list[str]:
    """Return a sorted list of all profile names in the vault."""
    vault = load_vault(vault_path, password)
    return sorted(vault.keys())
