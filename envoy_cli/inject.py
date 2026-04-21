"""Inject env values from a vault profile into a subprocess environment."""

from __future__ import annotations

import os
import subprocess
from typing import Dict, List, Optional

from envoy_cli.vault import load_vault


class InjectError(Exception):
    """Raised when injection fails."""


def build_env(
    vault_file: str,
    password: str,
    profile: str,
    keys: Optional[List[str]] = None,
    override: bool = True,
) -> Dict[str, str]:
    """Return a copy of os.environ merged with values from *profile*.

    Args:
        vault_file: Path to the vault file.
        password:   Vault password.
        profile:    Profile name to inject from.
        keys:       Optional allowlist of keys to inject.  ``None`` means all.
        override:   When *True* (default), vault values overwrite existing env
                    vars.  When *False*, existing vars are preserved.

    Returns:
        A new dict suitable for passing to ``subprocess.run(=...)``.  The
        current process environment is always included as the base.
    """
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise InjectError(f"Profile '{profile}' not found in vault.")

    profile_env: Dict[str, str] = vault[profile]

    if keys is not None:
        missing = [k for k in keys if k not in profile_env]
        if missing:
            raise InjectError(
                f"Keys not found in profile '{profile}': {', '.join(missing)}"
            )
        profile_env = {k: profile_env[k] for k in keys}

    merged = dict(os.environ)
    for key, value in profile_env.items():
        if override or key not in merged:
            merged[key] = value

    return merged


def inject_and_run(
    vault_file: str,
    password: str,
    profile: str,
    command: List[str],
    keys: Optional[List[str]] = None,
    override: bool = True,
) -> int:
    """Run *command* with the profile's env vars injected.

    Returns:
        The exit code of the subprocess.
    """
    if not command:
        raise InjectError("No command provided to run.")

    env = build_env(vault_file, password, profile, keys=keys, override=override)
    result = subprocess.run(command, env=env)  # noqa: S603
    return result.returncode
