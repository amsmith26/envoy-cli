"""Compare two profiles or env files across a vault."""

from typing import Dict, List, Tuple
from envoy_cli.vault import load_vault


ChangeType = str  # 'added' | 'removed' | 'changed' | 'unchanged'


def compare_profiles(
    vault_path: str,
    password: str,
    profile_a: str,
    profile_b: str,
) -> List[Dict]:
    """Return a list of comparison entries between two vault profiles."""
    vault = load_vault(vault_path, password)

    if profile_a not in vault:
        raise KeyError(f"Profile '{profile_a}' not found in vault.")
    if profile_b not in vault:
        raise KeyError(f"Profile '{profile_b}' not found in vault.")

    env_a: Dict[str, str] = vault[profile_a]
    env_b: Dict[str, str] = vault[profile_b]

    return _build_comparison(env_a, env_b)


def compare_env_to_profile(
    env: Dict[str, str],
    vault_path: str,
    password: str,
    profile: str,
) -> List[Dict]:
    """Compare a local env dict against a vault profile."""
    vault = load_vault(vault_path, password)

    if profile not in vault:
        raise KeyError(f"Profile '{profile}' not found in vault.")

    env_b: Dict[str, str] = vault[profile]
    return _build_comparison(env, env_b)


def _build_comparison(env_a: Dict[str, str], env_b: Dict[str, str]) -> List[Dict]:
    results = []
    all_keys = sorted(set(env_a) | set(env_b))

    for key in all_keys:
        in_a = key in env_a
        in_b = key in env_b

        if in_a and not in_b:
            change: ChangeType = "removed"
        elif not in_a and in_b:
            change = "added"
        elif env_a[key] != env_b[key]:
            change = "changed"
        else:
            change = "unchanged"

        results.append({
            "key": key,
            "change": change,
            "value_a": env_a.get(key),
            "value_b": env_b.get(key),
        })

    return results


def summary(comparison: List[Dict]) -> Tuple[int, int, int, int]:
    """Return (added, removed, changed, unchanged) counts."""
    counts = {"added": 0, "removed": 0, "changed": 0, "unchanged": 0}
    for entry in comparison:
        counts[entry["change"]] += 1
    return counts["added"], counts["removed"], counts["changed"], counts["unchanged"]
