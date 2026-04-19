"""Audit log for tracking vault operations."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any


def _audit_path(vault_path: str | Path) -> Path:
    p = Path(vault_path)
    return p.with_suffix(".audit.json")


def _load_log(vault_path: str | Path) -> List[Dict[str, Any]]:
    path = _audit_path(vault_path)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def _save_log(vault_path: str | Path, entries: List[Dict[str, Any]]) -> None:
    path = _audit_path(vault_path)
    path.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def record_event(
    vault_path: str | Path,
    action: str,
    profile: str,
    details: str = "",
) -> None:
    """Append an audit event to the log."""
    entries = _load_log(vault_path)
    entries.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "profile": profile,
            "details": details,
        }
    )
    _save_log(vault_path, entries)


def get_log(vault_path: str | Path) -> List[Dict[str, Any]]:
    """Return all audit log entries for a vault."""
    return _load_log(vault_path)


def clear_log(vault_path: str | Path) -> None:
    """Remove the audit log file."""
    path = _audit_path(vault_path)
    if path.exists():
        path.unlink()
