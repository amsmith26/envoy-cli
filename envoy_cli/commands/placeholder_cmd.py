"""CLI commands for placeholder key management."""

from __future__ import annotations

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_placeholder import (
    PlaceholderError,
    get_placeholder_keys,
    mark_placeholder,
    unmark_placeholder,
    get_placeholder_description,
    list_unset_placeholders,
)


@click.group("placeholder")
def placeholder() -> None:
    """Manage placeholder (not-yet-set) keys."""


@placeholder.command("mark")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.option("--description", "-d", default="", help="Optional description for this placeholder.")
def cmd_mark_placeholder(vault: str, password: str, profile: str, key: str, description: str) -> None:
    """Mark KEY in PROFILE as a placeholder."""
    try:
        keys = mark_placeholder(vault, password, profile, key, description)
        click.echo(f"Marked '{key}' as placeholder in '{profile}'.")
        click.echo("Placeholders: " + ", ".join(keys))
    except PlaceholderError as exc:
        raise click.ClickException(str(exc))


@placeholder.command("unmark")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_unmark_placeholder(vault: str, password: str, profile: str, key: str) -> None:
    """Remove placeholder mark from KEY in PROFILE."""
    try:
        keys = unmark_placeholder(vault, password, profile, key)
        click.echo(f"Removed placeholder mark from '{key}' in '{profile}'.")
        if keys:
            click.echo("Remaining placeholders: " + ", ".join(keys))
        else:
            click.echo("No placeholders remaining.")
    except PlaceholderError as exc:
        raise click.ClickException(str(exc))


@placeholder.command("list")
@vault_options
@click.argument("profile")
def cmd_list_placeholders(vault: str, password: str, profile: str) -> None:
    """List all placeholder keys in PROFILE."""
    keys = get_placeholder_keys(vault, password, profile)
    if not keys:
        click.echo(f"No placeholders defined for '{profile}'.")
        return
    for key in keys:
        desc = get_placeholder_description(vault, password, profile, key)
        suffix = f"  # {desc}" if desc else ""
        click.echo(f"  {key}{suffix}")


@placeholder.command("check")
@vault_options
@click.argument("profile")
def cmd_check_placeholders(vault: str, password: str, profile: str) -> None:
    """Show placeholder keys that still have empty values in PROFILE."""
    unset = list_unset_placeholders(vault, password, profile)
    if not unset:
        click.echo(f"All placeholders in '{profile}' have values set.")
        return
    click.echo(f"Unset placeholders in '{profile}':")
    for key in unset:
        click.echo(f"  {key}")
    raise SystemExit(1)
