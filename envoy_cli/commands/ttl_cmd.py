"""CLI commands for managing key TTLs."""
import click

from envoy_cli.commands import vault_options
from envoy_cli.env_ttl import TTLError, get_ttl, is_expired, list_ttls, purge_expired, remove_ttl, set_ttl


@click.group("ttl")
def ttl():
    """Manage time-to-live settings for keys."""


@ttl.command("set")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.option("--seconds", "-s", type=int, required=True, help="TTL in seconds.")
def cmd_set_ttl(vault_file, password, profile, key, seconds):
    """Set a TTL for KEY in PROFILE."""
    try:
        expiry = set_ttl(vault_file, password, profile, key, seconds)
        click.echo(f"TTL set for '{key}' in '{profile}'. Expires at: {expiry}")
    except TTLError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@ttl.command("get")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_get_ttl(vault_file, password, profile, key):
    """Show TTL expiry for KEY in PROFILE."""
    expiry = get_ttl(vault_file, password, profile, key)
    if expiry is None:
        click.echo(f"No TTL set for '{key}' in '{profile}'.")
    else:
        expired = is_expired(vault_file, password, profile, key)
        status = " [EXPIRED]" if expired else ""
        click.echo(f"{key}: {expiry}{status}")


@ttl.command("remove")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_remove_ttl(vault_file, password, profile, key):
    """Remove TTL for KEY in PROFILE."""
    removed = remove_ttl(vault_file, password, profile, key)
    if removed:
        click.echo(f"TTL removed for '{key}' in '{profile}'.")
    else:
        click.echo(f"No TTL was set for '{key}' in '{profile}'.")


@ttl.command("list")
@vault_options
@click.argument("profile")
def cmd_list_ttls(vault_file, password, profile):
    """List all TTLs for PROFILE."""
    ttls = list_ttls(vault_file, password, profile)
    if not ttls:
        click.echo(f"No TTLs set in '{profile}'.")
        return
    for key, expiry in ttls.items():
        expired = is_expired(vault_file, password, profile, key)
        status = " [EXPIRED]" if expired else ""
        click.echo(f"  {key}: {expiry}{status}")


@ttl.command("purge")
@vault_options
@click.argument("profile")
def cmd_purge_expired(vault_file, password, profile):
    """Remove all expired keys from PROFILE."""
    try:
        removed = purge_expired(vault_file, password, profile)
        if removed:
            click.echo(f"Purged {len(removed)} expired key(s): {', '.join(removed)}")
        else:
            click.echo("No expired keys found.")
    except TTLError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
