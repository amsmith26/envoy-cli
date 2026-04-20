"""CLI commands for pinning and unpinning keys in vault profiles."""

import click
from envoy_cli.pin import pin_key, unpin_key, get_pinned_keys, PinError
from envoy_cli.vault import load_vault, vault_exists


@click.group()
def pin():
    """Pin or unpin keys to protect them from being overwritten."""
    pass


@pin.command("add")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", "vault_file", default=".envoy_vault", show_default=True)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def cmd_pin_key(profile: str, key: str, vault_file: str, password: str):
    """Pin KEY in PROFILE so it won't be overwritten on pull/merge."""
    try:
        pins = pin_key(vault_file, password, profile, key)
        click.echo(f"Pinned '{key}' in profile '{profile}'.")
        click.echo(f"Pinned keys: {', '.join(pins)}")
    except PinError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pin.command("remove")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", "vault_file", default=".envoy_vault", show_default=True)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def cmd_unpin_key(profile: str, key: str, vault_file: str, password: str):
    """Unpin KEY in PROFILE."""
    try:
        pins = unpin_key(vault_file, password, profile, key)
        click.echo(f"Unpinned '{key}' from profile '{profile}'.")
        if pins:
            click.echo(f"Remaining pinned keys: {', '.join(pins)}")
        else:
            click.echo("No pinned keys remaining.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pin.command("list")
@click.argument("profile")
@click.option("--vault", "vault_file", default=".envoy_vault", show_default=True)
@click.password_option("--password", prompt="Vault password", confirmation_prompt=False)
def cmd_list_pins(profile: str, vault_file: str, password: str):
    """List all pinned keys for PROFILE."""
    if not vault_exists(vault_file):
        click.echo("No vault found.", err=True)
        raise SystemExit(1)
    vault = load_vault(vault_file, password)
    pins = get_pinned_keys(vault, profile)
    if not pins:
        click.echo(f"No pinned keys in profile '{profile}'.")
    else:
        click.echo(f"Pinned keys in '{profile}':")
        for k in pins:
            click.echo(f"  - {k}")
