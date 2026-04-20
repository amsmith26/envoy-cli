"""CLI commands for promoting env variables between profiles."""

import click
from envoy_cli.commands import vault_options
from envoy_cli.promote import promote_profile, list_promotable_keys, PromoteError
from envoy_cli.lock import LockError


@click.group()
def promote():
    """Promote variables from one profile to another."""


@promote.command("run")
@vault_options
@click.argument("source")
@click.argument("target")
@click.option("--key", "-k", multiple=True, help="Specific key(s) to promote. Repeatable.")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys that already exist in target.")
def cmd_promote(vault, password, source, target, key, no_overwrite):
    """Promote variables from SOURCE profile to TARGET profile."""
    keys = list(key) if key else None
    try:
        result = promote_profile(
            vault_file=vault,
            password=password,
            source=source,
            target=target,
            keys=keys,
            overwrite=not no_overwrite,
        )
    except PromoteError as e:
        raise click.ClickException(str(e))
    except LockError as e:
        raise click.ClickException(str(e))

    if result["promoted"]:
        click.echo(f"Promoted {len(result['promoted'])} key(s) from '{source}' to '{target}':")
        for k in result["promoted"]:
            click.echo(f"  + {k}")
    else:
        click.echo("No keys were promoted.")

    if result["skipped"]:
        click.echo(f"Skipped {len(result['skipped'])} key(s): {', '.join(result['skipped'])}")


@promote.command("preview")
@vault_options
@click.argument("source")
@click.argument("target")
def cmd_preview(vault, password, source, target):
    """Preview what would be promoted from SOURCE to TARGET without making changes."""
    try:
        result = list_promotable_keys(vault_file=vault, password=password, source=source, target=target)
    except PromoteError as e:
        raise click.ClickException(str(e))

    if not any(result.values()):
        click.echo(f"Source profile '{source}' has no keys.")
        return

    if result["new"]:
        click.echo("New keys (will be added):")
        for k in result["new"]:
            click.echo(f"  + {k}")

    if result["changed"]:
        click.echo("Changed keys (will be overwritten):")
        for k in result["changed"]:
            click.echo(f"  ~ {k}")

    if result["unchanged"]:
        click.echo("Unchanged keys (will be skipped):")
        for k in result["unchanged"]:
            click.echo(f"  = {k}")
