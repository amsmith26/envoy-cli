"""CLI commands for copying keys between profiles."""

import click
from envoy_cli.commands import vault_options
from envoy_cli.env_copy import copy_key, copy_keys, EnvCopyError


@click.group("copy")
def env_copy():
    """Copy keys between profiles."""


@env_copy.command("key")
@vault_options
@click.argument("src_profile")
@click.argument("dst_profile")
@click.argument("key")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing key.")
def cmd_copy_key(vault, password, src_profile, dst_profile, key, overwrite):
    """Copy a single KEY from SRC_PROFILE to DST_PROFILE."""
    try:
        value = copy_key(vault, password, src_profile, dst_profile, key, overwrite)
        click.echo(
            f"Copied '{key}' from '{src_profile}' to '{dst_profile}' (value: {value!r})."
        )
    except EnvCopyError as exc:
        raise click.ClickException(str(exc))


@env_copy.command("keys")
@vault_options
@click.argument("src_profile")
@click.argument("dst_profile")
@click.argument("keys", nargs=-1, required=True)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
def cmd_copy_keys(vault, password, src_profile, dst_profile, keys, overwrite):
    """Copy multiple KEYS from SRC_PROFILE to DST_PROFILE."""
    try:
        copied = copy_keys(
            vault, password, src_profile, dst_profile, list(keys), overwrite
        )
        for k, v in copied.items():
            click.echo(f"  {k}={v!r}")
        click.echo(
            f"Copied {len(copied)} key(s) from '{src_profile}' to '{dst_profile}'."
        )
    except EnvCopyError as exc:
        raise click.ClickException(str(exc))
