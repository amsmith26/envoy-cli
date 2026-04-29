"""CLI commands for freezing and unfreezing profiles."""
import click

from envoy_cli.commands import vault_options
from envoy_cli.env_freeze import (
    FreezeError,
    freeze_profile,
    get_frozen_profiles,
    is_frozen,
    unfreeze_profile,
)


@click.group("freeze")
def freeze() -> None:
    """Freeze or unfreeze profiles to prevent modifications."""


@freeze.command("lock")
@vault_options
@click.argument("profile")
def cmd_freeze_profile(vault: str, password: str, profile: str) -> None:
    """Freeze PROFILE to prevent modifications."""
    try:
        frozen = freeze_profile(vault, password, profile)
        click.echo(f"Profile '{profile}' is now frozen.")
        click.echo("Frozen profiles: " + ", ".join(frozen))
    except FreezeError as exc:
        raise click.ClickException(str(exc))


@freeze.command("unlock")
@vault_options
@click.argument("profile")
def cmd_unfreeze_profile(vault: str, password: str, profile: str) -> None:
    """Unfreeze PROFILE to allow modifications."""
    try:
        remaining = unfreeze_profile(vault, password, profile)
        click.echo(f"Profile '{profile}' has been unfrozen.")
        if remaining:
            click.echo("Still frozen: " + ", ".join(remaining))
        else:
            click.echo("No profiles are currently frozen.")
    except FreezeError as exc:
        raise click.ClickException(str(exc))


@freeze.command("list")
@vault_options
def cmd_list_frozen(vault: str, password: str) -> None:
    """List all frozen profiles."""
    try:
        frozen = get_frozen_profiles(vault, password)
        if not frozen:
            click.echo("No profiles are currently frozen.")
        else:
            for name in frozen:
                click.echo(name)
    except Exception as exc:
        raise click.ClickException(str(exc))


@freeze.command("check")
@vault_options
@click.argument("profile")
def cmd_check_frozen(vault: str, password: str, profile: str) -> None:
    """Check whether PROFILE is frozen."""
    try:
        if is_frozen(vault, password, profile):
            click.echo(f"Profile '{profile}' is frozen.")
        else:
            click.echo(f"Profile '{profile}' is not frozen.")
    except Exception as exc:
        raise click.ClickException(str(exc))
