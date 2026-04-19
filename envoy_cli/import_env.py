"""Import env variables from external sources like shell environment or docker-compose."""
from __future__ import annotations

import json
import os
import re
from typing import Dict, Optional


def import_from_shell(keys: Optional[list] = None) -> Dict[str, str]:
    """Import variables from the current shell environment.

    Args:
        keys: Optional list of keys to import. If None, imports all.

    Returns:
        Dict of env key/value pairs.
    """
    env = dict(os.environ)
    if keys:
        env = {k: env[k] for k in keys if k in env}
    return env


def import_from_json(json_str: str) -> Dict[str, str]:
    """Parse a JSON object string into an env dict.

    Args:
        json_str: A JSON string like '{"KEY": "value"}'.

    Returns:
        Dict of env key/value pairs.

    Raises:
        ValueError: If the JSON is invalid or not an object.
    """
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("JSON must be an object at the top level.")
    return {str(k): str(v) for k, v in data.items()}


def import_from_dotenv_string(raw: str) -> Dict[str, str]:
    """Parse a raw .env-formatted string into a dict.

    Supports comments, blank lines, and quoted values.

    Args:
        raw: Multi-line string in .env format.

    Returns:
        Dict of env key/value pairs.
    """
    result: Dict[str, str] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        result[key] = value
    return result


def import_env(source: str, fmt: str = "dotenv", keys: Optional[list] = None) -> Dict[str, str]:
    """Unified import entry point.

    Args:
        source: Raw string content or 'shell' sentinel.
        fmt: One of 'dotenv', 'json', 'shell'.
        keys: Optional key filter (used with shell format).

    Returns:
        Dict of env key/value pairs.

    Raises:
        ValueError: On unknown format.
    """
    if fmt == "dotenv":
        return import_from_dotenv_string(source)
    elif fmt == "json":
        return import_from_json(source)
    elif fmt == "shell":
        return import_from_shell(keys)
    else:
        raise ValueError(f"Unknown import format: '{fmt}'. Choose from dotenv, json, shell.")
