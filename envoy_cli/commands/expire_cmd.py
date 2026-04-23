"""CLI commands for managing key expiry / TTL."""

from __future__ import annotations

from datetime import datetime, timezone

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_expire import (
    ExpireError,
    get_expiry,
    list_all_expiries,
    list_expired,
    remove_expiry,
    set_expiry,
)

_DT_FORMATS = ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"]


def _parse_dt(value: str) -> datetime:
    for fmt in _DT_FORMATS:
        try:
            dt = datetime.strptime(value, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise click.BadParameter(f"Cannot parse date '{value}'. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ.")


@click.group("expire")
def expire() -> None:
    """Manage key expiry / TTL within a vault profile."""


@expire.command("set")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.argument("expires_at")
def cmd_set_expiry(vault: str, password: str, profile: str, key: str, expires_at: str) -> None:
    """Set expiry for KEY in PROFILE (EXPIRES_AT: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)."""
    try:
        dt = _parse_dt(expires_at)
        result = set_expiry(vault, password, profile, key, dt)
        click.echo(f"Expiry set: {key} expires at {result}")
    except ExpireError as exc:
        raise click.ClickException(str(exc))


@expire.command("get")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_get_expiry(vault: str, password: str, profile: str, key: str) -> None:
    """Show the expiry date for KEY in PROFILE."""
    try:
        dt = get_expiry(vault, password, profile, key)
        if dt is None:
            click.echo(f"No expiry set for '{key}'.")
        else:
            click.echo(dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
    except ExpireError as exc:
        raise click.ClickException(str(exc))


@expire.command("remove")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_remove_expiry(vault: str, password: str, profile: str, key: str) -> None:
    """Remove the expiry for KEY in PROFILE."""
    removed = remove_expiry(vault, password, profile, key)
    if removed:
        click.echo(f"Expiry removed for '{key}'.")
    else:
        click.echo(f"No expiry was set for '{key}'.")


@expire.command("list")
@vault_options
@click.argument("profile")
def cmd_list_expiries(vault: str, password: str, profile: str) -> None:
    """List all expiry dates for keys in PROFILE."""
    entries = list_all_expiries(vault, password, profile)
    if not entries:
        click.echo("No expiry dates set.")
        return
    for key, ts in sorted(entries.items()):
        click.echo(f"  {key}: {ts}")


@expire.command("check")
@vault_options
@click.argument("profile")
def cmd_check_expired(vault: str, password: str, profile: str) -> None:
    """List keys in PROFILE whose expiry has passed."""
    expired = list_expired(vault, password, profile)
    if not expired:
        click.echo("No expired keys.")
    else:
        click.echo("Expired keys:")
        for key in expired:
            click.echo(f"  {key}")
