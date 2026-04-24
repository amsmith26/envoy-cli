"""CLI commands for managing key links between profiles."""

from __future__ import annotations

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_link import LinkError, add_link, get_links, remove_link, resolve_links


@click.group("link")
def link() -> None:
    """Manage key links between profiles."""


@link.command("add")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.argument("src_profile")
@click.argument("src_key")
def cmd_add_link(
    vault: str, password: str, profile: str, key: str, src_profile: str, src_key: str
) -> None:
    """Link PROFILE.KEY to SRC_PROFILE.SRC_KEY."""
    try:
        add_link(vault, password, profile, key, src_profile, src_key)
        click.echo(f"Linked {profile}.{key} -> {src_profile}.{src_key}")
    except LinkError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@link.command("remove")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_remove_link(vault: str, password: str, profile: str, key: str) -> None:
    """Remove the link for PROFILE.KEY."""
    removed = remove_link(vault, password, profile, key)
    if removed:
        click.echo(f"Link removed: {profile}.{key}")
    else:
        click.echo(f"No link found for {profile}.{key}", err=True)
        raise SystemExit(1)


@link.command("list")
@vault_options
@click.argument("profile")
def cmd_list_links(vault: str, password: str, profile: str) -> None:
    """List all links defined for PROFILE."""
    links = get_links(vault, password)
    profile_links = links.get(profile, {})
    if not profile_links:
        click.echo(f"No links defined for profile '{profile}'.")
        return
    for key, ref in sorted(profile_links.items()):
        click.echo(f"  {key} -> {ref['src_profile']}.{ref['src_key']}")


@link.command("resolve")
@vault_options
@click.argument("profile")
def cmd_resolve_links(vault: str, password: str, profile: str) -> None:
    """Show the resolved env for PROFILE with linked values substituted."""
    try:
        env = resolve_links(vault, password, profile)
        for key, value in sorted(env.items()):
            if not key.startswith("__"):
                click.echo(f"{key}={value}")
    except LinkError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
