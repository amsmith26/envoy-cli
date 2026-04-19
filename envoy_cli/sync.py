"""Sync .env files across environments using vault profiles."""

from pathlib import Path
from typing import Optional

from envoy_cli.parser import parse_env_file, serialize_env, merge_env
from envoy_cli.file_handler import read_env_file, write_env_file, backup_env_file
from envoy_cli.vault import load_vault, save_vault, vault_exists


def list_profiles(vault_path: Path, password: str) -> list[str]:
    """Return all profile names stored in the vault."""
    if not vault_exists(vault_path):
        return []
    data = load_vault(vault_path, password)
    return list(data.keys())


def push_env(env_path: Path, vault_path: Path, password: str, profile: str) -> None:
    """Push local .env file into vault under the given profile."""
    raw = read_env_file(env_path)
    parsed = parse_env_file(raw)

    existing: dict = {}
    if vault_exists(vault_path):
        existing = load_vault(vault_path, password)

    existing[profile] = parsed
    save_vault(vault_path, existing, password)


def pull_env(
    env_path: Path,
    vault_path: Path,
    password: str,
    profile: str,
    merge: bool = False,
    backup: bool = True,
) -> None:
    """Pull a profile from the vault and write it to the local .env file."""
    data = load_vault(vault_path, password)

    if profile not in data:
        raise KeyError(f"Profile '{profile}' not found in vault.")

    incoming: dict[str, str] = data[profile]

    if merge and env_path.exists():
        raw = read_env_file(env_path)
        local = parse_env_file(raw)
        incoming = merge_env(local, incoming)

    if backup and env_path.exists():
        backup_env_file(env_path)

    write_env_file(env_path, serialize_env(incoming))


def delete_profile(vault_path: Path, password: str, profile: str) -> None:
    """Remove a profile from the vault."""
    data = load_vault(vault_path, password)
    if profile not in data:
        raise KeyError(f"Profile '{profile}' not found in vault.")
    del data[profile]
    save_vault(vault_path, data, password)
