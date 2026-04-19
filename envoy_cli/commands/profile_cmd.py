import click
from envoy_cli.sync import list_profiles, push_env, pull_env, delete_profile
from envoy_cli.file_handler import read_env_file, write_env_file
from envoy_cli.vault import vault_exists


@click.group()
def profile():
    """Manage named environment profiles in the vault."""
    pass


@profile.command("list")
@click.argument("vault_file")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
def cmd_list_profiles(vault_file, password):
    """List all profiles stored in the vault."""
    if not vault_exists(vault_file):
        click.echo(f"No vault found at {vault_file}", err=True)
        raise SystemExit(1)
    try:
        profiles = list_profiles(vault_file, password)
        if not profiles:
            click.echo("No profiles found.")
        else:
            for p in profiles:
                click.echo(f"  - {p}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profile.command("copy")
@click.argument("vault_file")
@click.argument("src_profile")
@click.argument("dst_profile")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
def cmd_copy_profile(vault_file, src_profile, dst_profile, password):
    """Copy one profile to another name within the vault."""
    if not vault_exists(vault_file):
        click.echo(f"No vault found at {vault_file}", err=True)
        raise SystemExit(1)
    try:
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".env") as tmp:
            tmp_path = tmp.name
        pull_env(vault_file, src_profile, tmp_path, password)
        env_data = read_env_file(tmp_path)
        push_env(vault_file, dst_profile, env_data, password)
        os.unlink(tmp_path)
        click.echo(f"Copied profile '{src_profile}' to '{dst_profile}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@profile.command("rename")
@click.argument("vault_file")
@click.argument("old_name")
@click.argument("new_name")
@click.option("--password", prompt=True, hide_input=True, help="Vault password")
def cmd_rename_profile(vault_file, old_name, new_name, password):
    """Rename a profile within the vault."""
    if not vault_exists(vault_file):
        click.echo(f"No vault found at {vault_file}", err=True)
        raise SystemExit(1)
    try:
        import tempfile, os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".env") as tmp:
            tmp_path = tmp.name
        pull_env(vault_file, old_name, tmp_path, password)
        env_data = read_env_file(tmp_path)
        push_env(vault_file, new_name, env_data, password)
        delete_profile(vault_file, old_name, password)
        os.unlink(tmp_path)
        click.echo(f"Renamed profile '{old_name}' to '{new_name}'.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
