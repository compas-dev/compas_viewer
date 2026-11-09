from types import SimpleNamespace
from unittest.mock import Mock

from compas.geometry import Translation
from compas_viewer.commands import builtin_commands
from compas_viewer.commands import redo
from compas_viewer.commands import transform_selected
from compas_viewer.commands import undo
from compas_viewer.uidefinitions import default_menu_items


def test_transform_selected_delegates_the_ordered_selection_to_viewer():
    first = object()
    second = object()
    selection = SimpleNamespace(objects=(first, second))
    viewer = SimpleNamespace(state=SimpleNamespace(selection=selection), transform_objects=Mock())
    transformation = Translation.from_vector([1, 2, 3])

    transform_selected(viewer, transformation)

    viewer.transform_objects.assert_called_once_with((first, second), transformation, space="world")


def test_transform_selected_delegates_an_empty_selection_for_a_runtime_noop():
    selection = SimpleNamespace(objects=())
    viewer = SimpleNamespace(state=SimpleNamespace(selection=selection), transform_objects=Mock())
    transformation = Translation.from_vector([1, 0, 0])

    transform_selected(viewer, transformation)

    viewer.transform_objects.assert_called_once_with((), transformation, space="world")


def test_undo_and_redo_delegate_to_viewer_history():
    viewer = SimpleNamespace(undo=Mock(return_value=True), redo=Mock(return_value=False))

    assert undo(viewer)
    assert not redo(viewer)
    viewer.undo.assert_called_once_with()
    viewer.redo.assert_called_once_with()


def test_transform_history_commands_are_registered():
    commands = builtin_commands()

    assert commands["viewer.transform_selected"].callback is transform_selected
    assert commands["viewer.undo"].callback is undo
    assert commands["viewer.redo"].callback is redo


def test_edit_menu_exposes_history_editing_and_deletion_commands_once():
    edit_menu = next(item for item in default_menu_items() if item["title"] == "Edit")

    assert edit_menu["items"] == [
        {"title": "Undo", "command": "viewer.undo"},
        {"title": "Redo", "command": "viewer.redo"},
        {"type": "separator"},
        {"title": "Modify Parameters...", "command": "viewer.modify_selected"},
        {"type": "separator"},
        {"title": "Delete Selected", "command": "viewer.delete_selected"},
    ]
    assert [item.get("command") for item in edit_menu["items"]].count("viewer.delete_selected") == 1
    assert builtin_commands()["viewer.delete_selected"].keybinding == "Delete"
