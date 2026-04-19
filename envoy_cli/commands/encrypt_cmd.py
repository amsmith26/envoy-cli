"""CLI command handlers for encrypt / decrypt operations."""

import getpass
import sys

from envoy_cli.file_handler import read_env_file
from envoy_cli.parser import parse_env_file
from envoy_cli.vault import save_vault, load_vault, vault_exists
from envoy_cli.file_handler import write_env_file
from envoy_cli.parser import serialize_env


def cmd_encrypt(env_path: str, password: Optional[str] = None) -> None:
    """Read a plain .env file and write an encrypted vault."""
    if password is None:
        password = getpass.getpass("Encryption password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.", file=sys.stderr)
            sys.exit(1)

    raw = read_env_file(env_path)
    env = parse_env_file(raw)
    vault_file = save_vault(env, password, env_path)
    print(f"Vault written to {vault_file}")


def cmd_decrypt(env_path: str, output_path: str, password: Optional[str] = None) -> None:
    """Decrypt a vault and write a plain .env file."""
    if not vault_exists(env_path):
        print(f"No vault found for {env_path}", file=sys.stderr)
        sys.exit(1)

    if password is None:
        password = getpass.getpass("Decryption password: ")

    try:
        env = load_vault(env_path, password)
    except Exception as exc:
        print(f"Decryption failed: {exc}", file=sys.stderr)
        sys.exit(1)

    write_env_file(output_path, serialize_env(env))
    print(f"Decrypted env written to {output_path}")


from typing import Optional  # noqa: E402 (keep import at module level in real code)
