"""Profile locking — prevent accidental writes to protected profiles."""

from __future__ import annotations

LOCK_KEY = "__locked_profiles__"


class LockError(Exception):
    pass


def get_locked_profiles(vault: dict) -> list[str]:
    """Return list of locked profile names."""
    return list(vault.get(LOCK_KEY, []))


def lock_profile(vault: dict, profile: str) -> list[str]:
    """Lock a profile. Returns updated locked list."""
    if profile not in vault:
        raise LockError(f"Profile '{profile}' does not exist.")
    locked = set(vault.get(LOCK_KEY, []))
    locked.add(profile)
    vault[LOCK_KEY] = sorted(locked)
    return vault[LOCK_KEY]


def unlock_profile(vault: dict, profile: str) -> list[str]:
    """Unlock a profile. Returns updated locked list."""
    locked = set(vault.get(LOCK_KEY, []))
    locked.discard(profile)
    vault[LOCK_KEY] = sorted(locked)
    return vault[LOCK_KEY]


def is_locked(vault: dict, profile: str) -> bool:
    """Return True if the profile is locked."""
    return profile in vault.get(LOCK_KEY, [])


def assert_unlocked(vault: dict, profile: str) -> None:
    """Raise LockError if the profile is locked."""
    if is_locked(vault, profile):
        raise LockError(
            f"Profile '{profile}' is locked. Unlock it before making changes."
        )
