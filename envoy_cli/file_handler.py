"""File I/O utilities for reading and writing .env files."""

import os
from pathlib import Path
from typing import Dict, Optional

from envoy_cli.parser import parse_env_file, serialize_env


def read_env_file(path: str) -> Dict[str, str]:
    """Read and parse a .env file from the given path."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f".env file not found: {path}")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    content = file_path.read_text(encoding="utf-8")
    return parse_env_file(content)


def write_env_file(path: str, env_vars: Dict[str, str], overwrite: bool = True) -> None:
    """Write env variables to a .env file."""
    file_path = Path(path)
    if file_path.exists() and not overwrite:
        raise FileExistsError(f"File already exists and overwrite=False: {path}")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    content = serialize_env(env_vars)
    file_path.write_text(content, encoding="utf-8")


def backup_env_file(path: str) -> Optional[str]:
    """Create a timestamped backup of an existing .env file."""
    import shutil
    from datetime import datetime
    file_path = Path(path)
    if not file_path.exists():
        return None
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    backup_path = str(file_path) + f".backup.{timestamp}"
    shutil.copy2(str(file_path), backup_path)
    return backup_path
