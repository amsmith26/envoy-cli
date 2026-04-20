"""CLI commands for merging profiles."""

import click
from envoy_cli.merge import merge_profiles, list_merge_candidates, MergeError
from envoy_cli.commands import vault_options


@click.group()
def merge():
    """Merge profiles together."""
    pass


@merge.command("run")
@vault_options
@click.argument("sources", nargs=-1, required=True)
@click.option("--into", "target", required=True, help="Target profile name.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.option("--keys", default=None, help="Comma-separated list of keys to merge.")
def cmd_merge(vault, password, sources, target, overwrite, keys):
    """Merge SOURCE profiles INTO a target profile."""
    key_list = [k.strip() for k in keys.split(",")] if keys else None
    try:
        result = merge_profiles(
            vault, password,
            list(sources), target,
            overwrite=overwrite,
            keys=key_list,
        )
    except MergeError as e:
        raise click.ClickException(str(e))

    added = result["added"]
    updated = result["updated"]

    if added:
        click.echo(f"Added {len(added)} key(s): {', '.join(added)}")
    if updated:
        click.echo(f"Updated {len(updated)} key(s): {', '.join(updated)}")
    if not added and not updated:
        click.echo("Nothing to merge — target is already up to date.")
    else:
        click.echo(f"Merged into profile '{target}'.")


@merge.command("preview")
@vault_options
@click.argument("source")
@click.option("--into", "target", required=True, help="Target profile name.")
def cmd_preview_merge(vault, password, source, target):
    """Preview what would change if SOURCE were merged INTO target."""
    try:
        result = list_merge_candidates(vault, password, source, target)
    except MergeError as e:
        raise click.ClickException(str(e))

    if result["would_add"]:
        click.echo("Would add:")
        for k in result["would_add"]:
            click.echo(f"  + {k}")
    if result["would_update"]:
        click.echo("Would update:")
        for k in result["would_update"]:
            click.echo(f"  ~ {k}")
    if not result["would_add"] and not result["would_update"]:
        click.echo("No changes would be made.")
