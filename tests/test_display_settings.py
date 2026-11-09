from types import SimpleNamespace

from PySide6.QtWidgets import QApplication

from compas.colors import Color
from compas_viewer.components.displaysetting import DisplaySetting
from compas_viewer.config import Config
from compas_viewer.scene.gridobject import GridObject
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import default_sidebar_items


def test_grid_supports_positive_odd_division_counts():
    grid = GridObject(framesize=(10.0, 7, 5.0, 3), linecolor=Color.grey())

    assert grid.nx == 7
    assert grid.ny == 3


def test_default_sidebar_contains_display_settings():
    item_types = [item["type"] for item in default_sidebar_items()]

    assert "DisplaySetting" in item_types


def test_display_settings_exclude_grid_controls(monkeypatch):
    app = QApplication.instance() or QApplication([])
    config = Config()
    state = ViewerState(config)
    renderer = SimpleNamespace(rendermode=config.renderer.rendermode, view=config.renderer.view)
    viewer = SimpleNamespace(config=config, state=state)
    monkeypatch.setattr(DisplaySetting, "viewer", property(lambda _self: viewer), raising=False)

    panel = DisplaySetting(SimpleNamespace(renderer=renderer))

    assert set(panel._state_controls) == {
        "renderer.rendermode",
        "renderer.view",
        "renderer.backgroundcolor",
        "renderer.selectioncolor",
    }
    assert all(not child.label.text().startswith("Grid") for child in panel.children)
    assert app is not None
