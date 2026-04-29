"""CLI commands for env key usage tracking."""

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_usage import UsageError, get_usage, get_profile_usage, record_access, reset_usage, top_keys


@click.group("usage")
def usage():
    """Track and inspect key access usage statistics."""


@usage.command("record")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_record_access(vault_file, password, profile, key):
    """Record an access event for KEY in PROFILE."""
    try:
        entry = record_access(vault_file, password, profile, key)
        click.echo(f"Recorded access for '{key}' (total: {entry['count']}).")
    except UsageError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@usage.command("show")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_show_usage(vault_file, password, profile, key):
    """Show usage stats for KEY in PROFILE."""
    try:
        entry = get_usage(vault_file, password, profile, key)
        if entry is None:
            click.echo(f"No usage recorded for '{key}'.")
        else:
            click.echo(f"Key:          {key}")
            click.echo(f"Access count: {entry['count']}")
            click.echo(f"First access: {entry['first_access']}")
            click.echo(f"Last access:  {entry['last_access']}")
    except UsageError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@usage.command("profile")
@vault_options
@click.argument("profile")
def cmd_profile_usage(vault_file, password, profile):
    """Show usage stats for all keys in PROFILE."""
    try:
        stats = get_profile_usage(vault_file, password, profile)
        if not stats:
            click.echo("No usage data recorded for this profile.")
            return
        for key, entry in sorted(stats.items()):
            click.echo(f"{key}: {entry['count']} access(es), last={entry['last_access']}")
    except UsageError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@usage.command("top")
@vault_options
@click.argument("profile")
@click.option("--n", default=5, show_default=True, help="Number of top keys to show.")
def cmd_top_keys(vault_file, password, profile, n):
    """Show the top-N most accessed keys in PROFILE."""
    try:
        results = top_keys(vault_file, password, profile, n)
        if not results:
            click.echo("No usage data recorded.")
            return
        for rank, entry in enumerate(results, 1):
            click.echo(f"{rank}. {entry['key']}: {entry['count']} access(es)")
    except UsageError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@usage.command("reset")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_reset_usage(vault_file, password, profile, key):
    """Reset usage stats for KEY in PROFILE."""
    removed = reset_usage(vault_file, password, profile, key)
    if removed:
        click.echo(f"Usage stats for '{key}' cleared.")
    else:
        click.echo(f"No usage stats found for '{key}'.")
