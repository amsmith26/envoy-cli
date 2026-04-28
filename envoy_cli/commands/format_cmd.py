"""CLI commands for env-format feature."""

from __future__ import annotations

import click
from envoy_cli.commands import vault_options
from envoy_cli.vault import load_vault, save_vault
from envoy_cli.env_format import (
    FormatError,
    list_formats,
    get_format,
    set_format,
    remove_format,
    format_profile,
)


@click.group("format")
def fmt():
    """Manage value format rules for env keys."""


@fmt.command("set")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.argument("format_name")
def cmd_set_format(vault_file, password, profile, key, format_name):
    """Assign a format rule to KEY in PROFILE."""
    vault = load_vault(vault_file, password)
    try:
        result = set_format(vault, profile, key, format_name)
        save_vault(vault_file, password, vault)
        click.echo(f"Format '{result}' set for '{key}' in '{profile}'.")
    except FormatError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@fmt.command("get")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_get_format(vault_file, password, profile, key):
    """Show the format rule for KEY in PROFILE."""
    vault = load_vault(vault_file, password)
    fmt_name = get_format(vault, profile, key)
    if fmt_name:
        click.echo(fmt_name)
    else:
        click.echo(f"No format set for '{key}' in '{profile}'.")


@fmt.command("remove")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_remove_format(vault_file, password, profile, key):
    """Remove the format rule for KEY in PROFILE."""
    vault = load_vault(vault_file, password)
    removed = remove_format(vault, profile, key)
    if removed:
        save_vault(vault_file, password, vault)
        click.echo(f"Format rule removed for '{key}' in '{profile}'.")
    else:
        click.echo(f"No format rule found for '{key}' in '{profile}'.")


@fmt.command("apply")
@vault_options
@click.argument("profile")
@click.option("--dry-run", is_flag=True, help="Preview changes without saving.")
def cmd_apply_format(vault_file, password, profile, dry_run):
    """Apply all format rules for PROFILE."""
    vault = load_vault(vault_file, password)
    try:
        changed = format_profile(vault, profile, dry_run=dry_run)
        if not changed:
            click.echo("No changes.")
            return
        for key, new_val in changed.items():
            click.echo(f"  {key} => {new_val}")
        if not dry_run:
            save_vault(vault_file, password, vault)
            click.echo(f"{len(changed)} key(s) formatted.")
        else:
            click.echo(f"(dry-run) {len(changed)} key(s) would be formatted.")
    except FormatError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@fmt.command("list")
def cmd_list_formats():
    """List available format names."""
    for name in list_formats():
        click.echo(name)
