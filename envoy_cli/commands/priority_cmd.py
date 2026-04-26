"""CLI commands for managing profile priorities."""

from __future__ import annotations

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_priority import (
    PriorityError,
    get_priority,
    list_priorities,
    remove_priority,
    resolve_priority_order,
    set_priority,
)


@click.group("priority")
def priority() -> None:
    """Manage profile resolution priority."""


@priority.command("set")
@click.argument("profile")
@click.argument("value", type=int)
@vault_options
def cmd_set_priority(profile: str, value: int, vault: str, password: str) -> None:
    """Assign a numeric priority to a profile (lower = resolved first)."""
    try:
        prio = set_priority(vault, password, profile, value)
        click.echo(f"Priority for '{profile}' set to {prio}.")
    except PriorityError as exc:
        raise click.ClickException(str(exc)) from exc


@priority.command("get")
@click.argument("profile")
@vault_options
def cmd_get_priority(profile: str, vault: str, password: str) -> None:
    """Show the priority assigned to a profile."""
    prio = get_priority(vault, password, profile)
    if prio is None:
        click.echo(f"No priority set for '{profile}'.")
    else:
        click.echo(f"{profile}: {prio}")


@priority.command("remove")
@click.argument("profile")
@vault_options
def cmd_remove_priority(profile: str, vault: str, password: str) -> None:
    """Remove the priority assignment from a profile."""
    removed = remove_priority(vault, password, profile)
    if removed:
        click.echo(f"Priority removed from '{profile}'.")
    else:
        click.echo(f"'{profile}' had no priority assigned.")


@priority.command("list")
@vault_options
def cmd_list_priorities(vault: str, password: str) -> None:
    """List all profiles with assigned priorities, sorted ascending."""
    entries = list_priorities(vault, password)
    if not entries:
        click.echo("No priorities assigned.")
        return
    for entry in entries:
        click.echo(f"{entry['priority']:>4}  {entry['profile']}")


@priority.command("order")
@vault_options
def cmd_resolve_order(vault: str, password: str) -> None:
    """Show full profile resolution order (ranked first, then unranked)."""
    order = resolve_priority_order(vault, password)
    if not order:
        click.echo("No profiles found.")
        return
    for idx, name in enumerate(order, start=1):
        click.echo(f"{idx:>3}. {name}")
