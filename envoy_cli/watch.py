"""Watch an .env file for changes and sync to a vault profile automatically."""

import time
import os
from pathlib import Path
from typing import Optional, Callable


def get_mtime(path: str) -> Optional[float]:
    try:
        return os.path.getmtime(path)
    except FileNotFoundError:
        return None


def watch_env_file(
    env_path: str,
    on_change: Callable[[str], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """
    Poll env_path every `interval` seconds. Call on_change(env_path) when
    the file's mtime changes. Stops after max_iterations if provided (useful
    for testing).
    """
    path = Path(env_path)
    last_mtime = get_mtime(env_path)
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval)
        current_mtime = get_mtime(env_path)
        if current_mtime is not None and current_mtime != last_mtime:
            last_mtime = current_mtime
            on_change(env_path)
        iterations += 1


def make_push_handler(vault_path: str, profile: str, password: str) -> Callable[[str], None]:
    """Return an on_change callback that pushes the env file to a vault profile."""
    from envoy_cli.sync import push_env
    from envoy_cli.audit import record_event

    def handler(env_path: str) -> None:
        push_env(env_path, vault_path, profile, password)
        record_event(vault_path, "watch-push", profile, {"source": env_path})

    return handler
