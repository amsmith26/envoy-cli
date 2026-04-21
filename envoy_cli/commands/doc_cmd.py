"""CLI commands for managing inline env-key documentation."""

from __future__ import annotations

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_docs import DocError, get_doc, list_docs, remove_doc, set_doc


@click.group("doc")
def doc() -> None:
    """Manage inline documentation for env keys."""


@doc.command("set")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.argument("text")
def cmd_set_doc(vault: str, password: str, profile: str, key: str, text: str) -> None:
    """Attach a doc string to KEY in PROFILE."""
    try:
        set_doc(vault, password, profile, key, text)
        click.echo(f"Doc set for '{key}' in profile '{profile}'.")
    except DocError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@doc.command("get")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_get_doc(vault: str, password: str, profile: str, key: str) -> None:
    """Show the doc string for KEY in PROFILE."""
    text = get_doc(vault, password, profile, key)
    if text is None:
        click.echo(f"No documentation found for '{key}' in profile '{profile}'.")
    else:
        click.echo(text)


@doc.command("remove")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_remove_doc(vault: str, password: str, profile: str, key: str) -> None:
    """Remove the doc string for KEY in PROFILE."""
    removed = remove_doc(vault, password, profile, key)
    if removed:
        click.echo(f"Doc removed for '{key}' in profile '{profile}'.")
    else:
        click.echo(f"No doc to remove for '{key}' in profile '{profile}'.")


@doc.command("list")
@vault_options
@click.argument("profile")
def cmd_list_docs(vault: str, password: str, profile: str) -> None:
    """List all documented keys in PROFILE."""
    docs = list_docs(vault, password, profile)
    if not docs:
        click.echo(f"No documentation found in profile '{profile}'.")
        return
    for key, text in sorted(docs.items()):
        click.echo(f"{key}: {text}")
