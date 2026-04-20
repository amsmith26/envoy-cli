"""CLI commands for viewing key and profile change history."""

import click
from envoy_cli.history import get_key_history, get_profile_history, clear_history
from envoy_cli.vault import load_vault, vault_exists


@click.group()
def history():
    """View change history for keys and profiles."""
    pass


@history.command("key")
@click.argument("profile")
@click.argument("key")
@click.option("--vault", "vault_path", default=".envoy-vault", show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--limit", default=10, show_default=True, help="Maximum number of history entries to show.")
def cmd_key_history(profile: str, key: str, vault_path: str, password: str, limit: int):
    """Show change history for a specific KEY in a PROFILE."""
    if not vault_exists(vault_path):
        click.echo(f"Vault not found: {vault_path}", err=True)
        raise SystemExit(1)

    try:
        vault = load_vault(vault_path, password)
    except Exception:
        click.echo("Failed to load vault. Wrong password?", err=True)
        raise SystemExit(1)

    entries = get_key_history(vault, profile, key)
    if not entries:
        click.echo(f"No history found for key '{key}' in profile '{profile}'.")
        return

    click.echo(f"History for '{key}' in profile '{profile}':")
    click.echo("-" * 48)
    for entry in entries[-limit:]:
        timestamp = entry.get("timestamp", "unknown")
        old_val = entry.get("old_value")
        new_val = entry.get("new_value")
        action = entry.get("action", "changed")
        old_display = repr(old_val) if old_val is not None else "(none)"
        new_display = repr(new_val) if new_val is not None else "(none)"
        click.echo(f"  [{timestamp}] {action}: {old_display} → {new_display}")


@history.command("profile")
@click.argument("profile")
@click.option("--vault", "vault_path", default=".envoy-vault", show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--limit", default=20, show_default=True, help="Maximum number of history entries to show.")
def cmd_profile_history(profile: str, vault_path: str, password: str, limit: int):
    """Show all recorded changes for a PROFILE."""
    if not vault_exists(vault_path):
        click.echo(f"Vault not found: {vault_path}", err=True)
        raise SystemExit(1)

    try:
        vault = load_vault(vault_path, password)
    except Exception:
        click.echo("Failed to load vault. Wrong password?", err=True)
        raise SystemExit(1)

    entries = get_profile_history(vault, profile)
    if not entries:
        click.echo(f"No history recorded for profile '{profile}'.")
        return

    click.echo(f"Change history for profile '{profile}':")
    click.echo("-" * 56)
    for entry in entries[-limit:]:
        timestamp = entry.get("timestamp", "unknown")
        key = entry.get("key", "?")
        action = entry.get("action", "changed")
        old_val = entry.get("old_value")
        new_val = entry.get("new_value")
        old_display = repr(old_val) if old_val is not None else "(none)"
        new_display = repr(new_val) if new_val is not None else "(none)"
        click.echo(f"  [{timestamp}] {key}: {action} {old_display} → {new_display}")


@history.command("clear")
@click.argument("profile")
@click.option("--vault", "vault_path", default=".envoy-vault", show_default=True, help="Path to vault file.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.confirmation_option(prompt="Are you sure you want to clear history for this profile?")
def cmd_clear_history(profile: str, vault_path: str, password: str):
    """Clear all recorded history for a PROFILE."""
    if not vault_exists(vault_path):
        click.echo(f"Vault not found: {vault_path}", err=True)
        raise SystemExit(1)

    try:
        vault = load_vault(vault_path, password)
    except Exception:
        click.echo("Failed to load vault. Wrong password?", err=True)
        raise SystemExit(1)

    from envoy_cli.vault import save_vault
    cleared = clear_history(vault, profile)
    if cleared:
        save_vault(vault_path, password, vault)
        click.echo(f"History cleared for profile '{profile}'.")
    else:
        click.echo(f"No history found for profile '{profile}'.")
