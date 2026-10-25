import pytest

from compas_viewer.config import Config
from compas_viewer.components.menubar import MenuBar
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import default_menu_items


class Action:
    def __init__(self):
        self.checked = False

    def setChecked(self, checked):
        self.checked = checked


def test_state_updates_config_and_publishes_changes():
    config = Config()
    state = ViewerState(config)
    changes = []
    state.changed.connect(lambda path, value: changes.append((path, value)))

    changed = state.set("renderer.show_grid", False)

    assert changed
    assert not config.renderer.show_grid
    assert changes == [("renderer.show_grid", False)]


def test_state_does_not_publish_unchanged_values():
    state = ViewerState(Config())
    changes = []
    state.changed.connect(lambda path, value: changes.append((path, value)))

    changed = state.set("renderer.show_grid", True)

    assert not changed
    assert changes == []


def test_state_toggles_boolean_values():
    state = ViewerState(Config())

    assert not state.toggle("renderer.show_grid")
    assert not state.get("renderer.show_grid")


def test_state_rejects_invalid_paths_and_non_boolean_toggles():
    state = ViewerState(Config())

    with pytest.raises(ValueError, match="Invalid state path"):
        state.get("")
    with pytest.raises(TypeError, match="not boolean"):
        state.toggle("unit")


def test_menu_actions_reflect_published_state():
    action = Action()
    menubar = type("Menu", (), {"_state_actions": {"renderer.show_grid": [(action, True)]}})()

    MenuBar._on_state_changed(menubar, "renderer.show_grid", True)
    assert action.checked

    MenuBar._on_state_changed(menubar, "renderer.show_grid", False)
    assert not action.checked


def test_grid_menu_item_declares_its_state_binding():
    view_menu = next(item for item in default_menu_items() if item.get("title") == "View")
    grid_item = next(item for item in view_menu["items"] if item.get("title") == "Grid")

    assert grid_item["state"] == "renderer.show_grid"
