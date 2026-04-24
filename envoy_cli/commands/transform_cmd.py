"""CLI commands for transforming env values."""

import click
from envoy_cli.commands import vault_options
from envoy_cli.env_transform import (
    TransformError,
    apply_transform,
    list_transforms,
    transform_key,
    transform_profile,
)


@click.group("transform")
def transform():
    """Transform env values using built-in functions."""


@transform.command("key")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.argument("transform_name")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without saving.")
def cmd_transform_key(vault, password, profile, key, transform_name, dry_run):
    """Apply TRANSFORM_NAME to a single KEY in PROFILE."""
    try:
        old, new = transform_key(vault, password, profile, key, transform_name, dry_run=dry_run)
        prefix = "[dry-run] " if dry_run else ""
        click.echo(f"{prefix}{key}: {old!r} -> {new!r}")
    except TransformError as exc:
        raise click.ClickException(str(exc))


@transform.command("profile")
@vault_options
@click.argument("profile")
@click.argument("transform_name")
@click.option("--key", "keys", multiple=True, help="Restrict to specific keys (repeatable).")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without saving.")
def cmd_transform_profile(vault, password, profile, transform_name, keys, dry_run):
    """Apply TRANSFORM_NAME to all (or selected) keys in PROFILE."""
    try:
        results = transform_profile(
            vault, password, profile, transform_name,
            keys=list(keys) if keys else None,
            dry_run=dry_run,
        )
        prefix = "[dry-run] " if dry_run else ""
        for k, (old, new) in results.items():
            click.echo(f"{prefix}{k}: {old!r} -> {new!r}")
        click.echo(f"\n{prefix}Transformed {len(results)} key(s).")
    except TransformError as exc:
        raise click.ClickException(str(exc))


@transform.command("preview")
@click.argument("value")
@click.argument("transform_name")
def cmd_preview_transform(value, transform_name):
    """Preview applying TRANSFORM_NAME to VALUE without touching a vault."""
    try:
        result = apply_transform(value, transform_name)
        click.echo(f"{value!r} -> {result!r}")
    except TransformError as exc:
        raise click.ClickException(str(exc))


@transform.command("list")
def cmd_list_transforms():
    """List all available built-in transform names."""
    for name in list_transforms():
        click.echo(name)
