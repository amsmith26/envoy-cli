"""CLI commands for managing profile categories."""

import click

from envoy_cli.commands import vault_options
from envoy_cli.env_category import (
    CategoryError,
    get_category,
    list_by_category,
    list_uncategorized,
    remove_category,
    set_category,
)


@click.group("category")
def category():
    """Manage profile categories."""


@category.command("set")
@vault_options
@click.argument("profile")
@click.argument("category_name")
def cmd_set_category(vault, password, profile, category_name):
    """Assign CATEGORY_NAME to PROFILE."""
    try:
        cat = set_category(vault, password, profile, category_name)
        click.echo(f"Profile '{profile}' assigned to category '{cat}'.")
    except CategoryError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@category.command("get")
@vault_options
@click.argument("profile")
def cmd_get_category(vault, password, profile):
    """Show the category assigned to PROFILE."""
    cat = get_category(vault, password, profile)
    if cat is None:
        click.echo(f"Profile '{profile}' has no category assigned.")
    else:
        click.echo(cat)


@category.command("remove")
@vault_options
@click.argument("profile")
def cmd_remove_category(vault, password, profile):
    """Remove the category from PROFILE."""
    removed = remove_category(vault, password, profile)
    if removed:
        click.echo(f"Category removed from profile '{profile}'.")
    else:
        click.echo(f"Profile '{profile}' had no category set.")


@category.command("list")
@vault_options
def cmd_list_categories(vault, password):
    """List all profiles grouped by category."""
    by_cat = list_by_category(vault, password)
    if not by_cat:
        click.echo("No categories assigned.")
        return
    for cat, profiles in sorted(by_cat.items()):
        click.echo(f"[{cat}]")
        for p in profiles:
            click.echo(f"  {p}")


@category.command("uncategorized")
@vault_options
def cmd_list_uncategorized(vault, password):
    """List profiles with no category assigned."""
    profiles = list_uncategorized(vault, password)
    if not profiles:
        click.echo("All profiles have a category assigned.")
    else:
        for p in profiles:
            click.echo(p)
