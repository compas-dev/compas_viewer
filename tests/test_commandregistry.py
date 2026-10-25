import pytest

from compas_viewer.commandregistry import CommandRegistry
from compas_viewer.commands import Command
from compas_viewer.commands import builtin_commands
from compas_viewer.uidefinitions import UIItem
from compas_viewer.uidefinitions import default_menu_items


def _command_ids(items: list[UIItem]):
    for item in items:
        if command := item.get("command"):
            yield command
        yield from _command_ids(item.get("items", []))


def test_builtin_menu_commands_resolve_through_registry():
    registry = CommandRegistry(builtin_commands())

    assert all(command_id in registry for command_id in _command_ids(default_menu_items()))


def test_registry_rejects_duplicate_command_identifiers():
    command = Command(title="Example", callback=lambda viewer: viewer)
    registry = CommandRegistry({"example.command": command})

    with pytest.raises(ValueError, match="already registered"):
        registry.register("example.command", command)


def test_registry_can_replace_a_command_explicitly():
    first = Command(title="First", callback=lambda viewer: viewer)
    second = Command(title="Second", callback=lambda viewer: viewer)
    registry = CommandRegistry({"example.command": first})

    registry.register("example.command", second, replace=True)

    assert registry["example.command"] is second
