"""Parser for .env files — reads and writes key-value pairs."""

from typing import Dict, Tuple


def parse_env_file(content: str) -> Dict[str, str]:
    """Parse .env file content into a dictionary."""
    env_vars: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        value = _strip_quotes(value)
        if key:
            env_vars[key] = value
    return env_vars


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def serialize_env(env_vars: Dict[str, str]) -> str:
    """Serialize a dictionary back into .env file content."""
    lines = []
    for key, value in sorted(env_vars.items()):
        if any(c in value for c in (" ", "#", "'", '"')):
            value = f'"{value}"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + "\n"


def merge_env(base: Dict[str, str], override: Dict[str, str]) -> Tuple[Dict[str, str], list]:
    """Merge two env dicts; override takes precedence. Returns merged dict and list of changed keys."""
    merged = {**base}
    changed = []
    for key, value in override.items():
        if merged.get(key) != value:
            changed.append(key)
        merged[key] = value
    return merged, changed
