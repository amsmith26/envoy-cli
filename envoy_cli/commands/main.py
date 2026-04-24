"""Main CLI entry point for envoy-cli."""

import click

from envoy_cli.commands.archive_cmd import archive
from envoy_cli.commands.audit_cmd import audit
from envoy_cli.commands.diff_cmd import diff
from envoy_cli.commands.doc_cmd import doc
from envoy_cli.commands.encrypt_cmd import cmd_decrypt, cmd_encrypt
from envoy_cli.commands.env_copy_cmd import env_copy
from envoy_cli.commands.env_set_cmd import env_set
from envoy_cli.commands.expire_cmd import expire
from envoy_cli.commands.export_cmd import export
from envoy_cli.commands.group_cmd import group
from envoy_cli.commands.history_cmd import history
from envoy_cli.commands.import_cmd import cmd_import_profile
from envoy_cli.commands.lint_cmd import lint
from envoy_cli.commands.link_cmd import link
from envoy_cli.commands.mask_cmd import mask
from envoy_cli.commands.merge_cmd import merge
from envoy_cli.commands.pin_cmd import pin
from envoy_cli.commands.profile_cmd import profile
from envoy_cli.commands.promote_cmd import promote
from envoy_cli.commands.resolve_cmd import resolve
from envoy_cli.commands.rotate_cmd import cmd_rotate
from envoy_cli.commands.schema_cmd import schema
from envoy_cli.commands.scope_cmd import scope
from envoy_cli.commands.snapshot_cmd import snapshot
from envoy_cli.commands.sync_cmd import sync
from envoy_cli.commands.tag_cmd import tag
from envoy_cli.commands.template_cmd import template
from envoy_cli.commands.transform_cmd import transform
from envoy_cli.commands.validate_cmd import validate


@click.group()
@click.version_option()
def cli() -> None:
    """envoy-cli — manage and sync .env files securely."""


cli.add_command(archive)
cli.add_command(audit)
cli.add_command(diff)
cli.add_command(doc)
cli.add_command(cmd_encrypt, name="encrypt")
cli.add_command(cmd_decrypt, name="decrypt")
cli.add_command(env_copy)
cli.add_command(env_set)
cli.add_command(expire)
cli.add_command(export)
cli.add_command(group)
cli.add_command(history)
cli.add_command(cmd_import_profile, name="import")
cli.add_command(lint)
cli.add_command(link)
cli.add_command(mask)
cli.add_command(merge)
cli.add_command(pin)
cli.add_command(profile)
cli.add_command(promote)
cli.add_command(resolve)
cli.add_command(cmd_rotate, name="rotate")
cli.add_command(schema)
cli.add_command(scope)
cli.add_command(snapshot)
cli.add_command(sync)
cli.add_command(tag)
cli.add_command(template)
cli.add_command(transform)
cli.add_command(validate)
