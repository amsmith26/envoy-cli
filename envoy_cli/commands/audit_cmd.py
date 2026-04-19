"""CLI commands for viewing the audit log."""

from __future__ import annotations

import click

from envoy_cli.vault import _vault_path
from envoy_cli.audit import get_log, clear_log


@click.group()
def audit() -> None:
    """Audit log commands."""


@audit.command("log")
@click.option("--env-file", default=".env", show_default=True, help="Path to .env file.")
@click.option("--profile", default=None, help="Filter by profile name.")
@click.option("--limit", default=None, type=int, help="Limit number of entries shown.")
def cmd_show_log(env_file: str, profile: str | None, limit: int | None) -> None:
    """Show audit log entries for the vault."""
    vault = _vault_path(env_file)
    entries = get_log(vault)
    if not entries:
        click.echo("No audit log entries found.")
        return
    if profile:
        entries = [e for e in entries if e["profile"] == profile]
        if not entries:
            click.echo(f"No entries for profile '{profile}'.")
            return
    if limit is not None:
        entries = entries[-limit:]
    for e in entries:
        detail = f" ({e['details']}" + ")" if e["details"] else ""
        click.echo(f"[{e['timestamp']}] {e['action']:10s} profile={e['profile']}{detail}")


@audit.command("clear")
@click.option("--env-file", default=".env", show_default=True, help="Path to .env file.")
@click.confirmation_option(prompt="Are you sure you want to clear the audit log?")
def cmd_clear_log(env_file: str) -> None:
    """Clear the audit log for the vault."""
    vault = _vault_path(env_file)
    clear_log(vault)
    click.echo("Audit log cleared.")
