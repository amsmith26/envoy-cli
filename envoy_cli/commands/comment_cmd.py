"""CLI commands for managing inline key comments."""

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_comment import CommentError, get_comment, list_comments, remove_comment, set_comment


@click.group("comment")
def comment() -> None:
    """Manage inline comments for env keys."""


@comment.command("set")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.argument("text")
def cmd_set_comment(vault: str, password: str, profile: str, key: str, text: str) -> None:
    """Set an inline comment for KEY in PROFILE."""
    try:
        result = set_comment(vault, password, profile, key, text)
        click.echo(f"Comment set: {result}")
    except CommentError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@comment.command("get")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_get_comment(vault: str, password: str, profile: str, key: str) -> None:
    """Get the inline comment for KEY in PROFILE."""
    try:
        result = get_comment(vault, password, profile, key)
        if result is None:
            click.echo("(no comment)")
        else:
            click.echo(result)
    except CommentError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@comment.command("remove")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_remove_comment(vault: str, password: str, profile: str, key: str) -> None:
    """Remove the inline comment for KEY in PROFILE."""
    try:
        removed = remove_comment(vault, password, profile, key)
        click.echo("Comment removed." if removed else "No comment to remove.")
    except CommentError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@comment.command("list")
@vault_options
@click.argument("profile")
def cmd_list_comments(vault: str, password: str, profile: str) -> None:
    """List all inline comments for PROFILE."""
    try:
        comments = list_comments(vault, password, profile)
        if not comments:
            click.echo("No comments set.")
        else:
            for key, text in sorted(comments.items()):
                click.echo(f"{key}: {text}")
    except CommentError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
