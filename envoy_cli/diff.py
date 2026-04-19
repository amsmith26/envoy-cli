"""Diff utilities for comparing .env files or profiles."""

from typing import Dict, Tuple, List


DiffResult = Dict[str, Tuple[str, str]]  # key -> (old_val, new_val)


def diff_envs(base: Dict[str, str], target: Dict[str, str]) -> Dict[str, DiffResult]:
    """Compare two env dicts and return added, removed, and changed keys."""
    added: DiffResult = {}
    removed: DiffResult = {}
    changed: DiffResult = {}

    all_keys = set(base) | set(target)

    for key in all_keys:
        if key not in base:
            added[key] = ("", target[key])
        elif key not in target:
            removed[key] = (base[key], "")
        elif base[key] != target[key]:
            changed[key] = (base[key], target[key])

    return {"added": added, "removed": removed, "changed": changed}


def format_diff(diff: Dict[str, DiffResult]) -> List[str]:
    """Format a diff result into human-readable lines."""
    lines: List[str] = []

    for key, (_, new_val) in diff["added"].items():
        lines.append(f"+ {key}={new_val}")

    for key, (old_val, _) in diff["removed"].items():
        lines.append(f"- {key}={old_val}")

    for key, (old_val, new_val) in diff["changed"].items():
        lines.append(f"~ {key}: {old_val!r} -> {new_val!r}")

    return lines


def has_changes(diff: Dict[str, DiffResult]) -> bool:
    """Return True if any differences exist."""
    return any(diff[section] for section in ("added", "removed", "changed"))
