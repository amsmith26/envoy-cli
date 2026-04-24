"""CLI commands for masking/unmasking sensitive env keys."""

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_mask import MaskError, get_masked_keys, mask_key, unmask_key, apply_masks
from envoy_cli.vault import load_vault


@click.group("mask")
def mask():
    """Mask or unmask sensitive keys so their values are redacted in output."""


@mask.command("add")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_mask_key(vault_file, password, profile, key):
    """Mark KEY in PROFILE as masked (value hidden in output)."""
    try:
        result = mask_key(vault_file, password, profile, key)
        click.echo(f"Masked keys in '{profile}': {', '.join(result)}")
    except MaskError as exc:
        raise click.ClickException(str(exc))


@mask.command("remove")
@vault_options
@click.argument("profile")
@click.argument("key")
def cmd_unmask_key(vault_file, password, profile, key):
    """Remove mask from KEY in PROFILE."""
    try:
        result = unmask_key(vault_file, password, profile, key)
        if result:
            click.echo(f"Masked keys in '{profile}': {', '.join(result)}")
        else:
            click.echo(f"No masked keys remaining in '{profile}'.")
    except MaskError as exc:
        raise click.ClickException(str(exc))


@mask.command("list")
@vault_options
@click.argument("profile")
def cmd_list_masked(vault_file, password, profile):
    """List all masked keys for PROFILE."""
    vault = load_vault(vault_file, password)
    keys = get_masked_keys(vault, profile)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No masked keys in '{profile}'.")


@mask.command("show")
@vault_options
@click.argument("profile")
@click.option("--placeholder", default="***", show_default=True, help="Replacement text for masked values.")
def cmd_show_masked(vault_file, password, profile, placeholder):
    """Display env for PROFILE with masked values redacted."""
    vault = load_vault(vault_file, password)
    if profile not in vault:
        raise click.ClickException(f"Profile '{profile}' not found.")
    env = {k: v for k, v in vault[profile].items() if not k.startswith("__")}
    masked_keys = get_masked_keys(vault, profile)
    redacted = apply_masks(env, masked_keys, placeholder)
    for k, v in redacted.items():
        click.echo(f"{k}={v}")
