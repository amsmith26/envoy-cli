"""CLI commands for tagging profiles."""
import click
from envoy_cli.vault import load_vault, save_vault, vault_exists
from envoy_cli.tag import add_tag, remove_tag, get_tags, list_profiles_by_tag, TagError


@click.group()
def tag():
    """Tag profiles for organization."""
    pass


@tag.command("add")
@click.argument("profile")
@click.argument("tag_name")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_add_tag(profile, tag_name, vault_path, password):
    """Add a tag to a profile."""
    if not vault_exists(vault_path):
        click.echo("No vault found.", err=True)
        raise SystemExit(1)
    vault = load_vault(vault_path, password)
    try:
        updated = add_tag(vault, profile, tag_name)
        save_vault(vault_path, vault, password)
        click.echo(f"Tagged '{profile}' with '{tag_name}'. Tags: {updated}")
    except TagError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@tag.command("remove")
@click.argument("profile")
@click.argument("tag_name")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_remove_tag(profile, tag_name, vault_path, password):
    """Remove a tag from a profile."""
    if not vault_exists(vault_path):
        click.echo("No vault found.", err=True)
        raise SystemExit(1)
    vault = load_vault(vault_path, password)
    try:
        updated = remove_tag(vault, profile, tag_name)
        save_vault(vault_path, vault, password)
        click.echo(f"Removed tag '{tag_name}' from '{profile}'. Tags: {updated}")
    except TagError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@tag.command("list")
@click.argument("profile")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_list_tags(profile, vault_path, password):
    """List tags for a profile."""
    if not vault_exists(vault_path):
        click.echo("No vault found.", err=True)
        raise SystemExit(1)
    vault = load_vault(vault_path, password)
    tags = get_tags(vault, profile)
    if tags:
        click.echo(", ".join(tags))
    else:
        click.echo(f"No tags for '{profile}'.")


@tag.command("filter")
@click.argument("tag_name")
@click.option("--vault", "vault_path", default=".env.vault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def cmd_filter_by_tag(tag_name, vault_path, password):
    """List profiles that have a given tag."""
    if not vault_exists(vault_path):
        click.echo("No vault found.", err=True)
        raise SystemExit(1)
    vault = load_vault(vault_path, password)
    profiles = list_profiles_by_tag(vault, tag_name)
    if profiles:
        for p in profiles:
            click.echo(p)
    else:
        click.echo(f"No profiles tagged with '{tag_name}'.")
