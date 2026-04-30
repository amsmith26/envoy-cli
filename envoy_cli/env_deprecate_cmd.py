import click
from envoy_cli.commands import vault_options
from envoy_cli.vault import load_vault, save_vault
from envoy_cli.env_deprecate import (
    deprecate_key,
    undeprecate_key,
    get_deprecations,
    DeprecateError,
)


@click.group(name="deprecate")
def deprecate():
    """Manage key deprecation notices."""


@deprecate.command("set")
@vault_options
@click.argument("profile")
@click.argument("key")
@click.option("--reason", "-r", default="", help="Reason for deprecation.")
@click.option("--replacement", "-R", default="", help="Suggested replacement key.")
def cmd_deprecate_key(vault_file, password, profile, key, reason, replacement):
    """Mark a key as deprecated."""
    vault = load_vault(vault_file, password)
    try:
        record = deprecate_key(vault, profile, key, reason=reason, replacement=replacement)
        save_vault(vault_file, password, vault)
        click.echo(f"Deprecated '{key}' in profile '{profile}'.")
        if record.get("reason"):
            click.echo(f"  Reason: {record['reason']}")
        if record.get("replacement"):
            click.echo(f"  Replacement: {record['replacement']}")
    except DeprecateError as exc:
        raise click.ClickException(str(exc))


@deprecate.command("unset")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_undeprecate_key(vault_file, password, profile, key):
    """Remove a deprecation notice from a key."""
    vault = load_vault(vault_file, password)
    try:
        undeprecate_key(vault, profile, key)
        save_vault(vault_file, password, vault)
        click.echo(f"Removed deprecation for '{key}' in profile '{profile}'.")
    except DeprecateError as exc:
        raise click.ClickException(str(exc))


@deprecate.command("list")
@vault_options
@click.argument("profile")
def cmd_list_deprecations(vault_file, password, profile):
    """List all deprecated keys in a profile."""
    vault = load_vault(vault_file, password)
    try:
        deps = get_deprecations(vault, profile)
        if not deps:
            click.echo(f"No deprecated keys in profile '{profile}'.")
            return
        for key, record in sorted(deps.items()):
            parts = [f"  {key}"]
            if record.get("reason"):
                parts.append(f"reason={record['reason']}")
            if record.get("replacement"):
                parts.append(f"replacement={record['replacement']}")
            click.echo("  ".join(parts))
    except DeprecateError as exc:
        raise click.ClickException(str(exc))
