"""Export env profiles to various formats (shell, docker, json)."""

import json
from typing import Dict

SUPPORTED_FORMATS = ("shell", "docker", "json")


def export_as_shell(env: Dict[str, str]) -> str:
    """Export env vars as shell export statements."""
    lines = []
    for key, value in env.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'export {key}="{escaped}"')
    return "\n".join(lines)


def export_as_docker(env: Dict[str, str]) -> str:
    """Export env vars as docker --env-file compatible format."""
    lines = []
    for key, value in env.items():
        lines.append(f"{key}={value}")
    return "\n".join(lines)


def export_as_json(env: Dict[str, str]) -> str:
    """Export env vars as a JSON object."""
    return json.dumps(env, indent=2)


def export_env(env: Dict[str, str], fmt: str) -> str:
    """Export env dict to the given format string."""
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}")
    if fmt == "shell":
        return export_as_shell(env)
    if fmt == "docker":
        return export_as_docker(env)
    if fmt == "json":
        return export_as_json(env)
