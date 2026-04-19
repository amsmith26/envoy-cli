"""Vault: read/write encrypted .env vault files on disk."""

import json
from pathlib import Path
from typing import Optional

from envoy_cli.crypto import encrypt_env, decrypt_env
from envoy_cli.file_handler import backup_env_file

VAULT_EXTENSION = ".vault"


def _vault_path(env_path: str) -> Path:
    p = Path(env_path)
    return p.with_suffix(VAULT_EXTENSION)


def save_vault(env: dict, password: str, path: str, backup: bool = True) -> Path:
    """Encrypt env dict and write to a vault file next to the source."""
    vault_file = _vault_path(path)
    if backup and vault_file.exists():
        backup_env_file(str(vault_file))
    encrypted = encrypt_env(env, password)
    vault_file.write_text(json.dumps(encrypted, indent=2), encoding="utf-8")
    return vault_file


def load_vault(path: str, password: str) -> dict:
    """Load and decrypt a vault file, returning a plain env dict."""
    vault_file = _vault_path(path)
    if not vault_file.exists():
        raise FileNotFoundError(f"Vault file not found: {vault_file}")
    encrypted = json.loads(vault_file.read_text(encoding="utf-8"))
    return decrypt_env(encrypted, password)


def vault_exists(path: str) -> bool:
    """Return True if a vault file exists for the given env path."""
    return _vault_path(path).exists()
