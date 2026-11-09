from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QMainWindow

from compas_viewer.components.displaysetting import DisplaySetting
from compas_viewer.components.menubar import MenuBar
from compas_viewer.components.toolbar import ToolBar
from compas_viewer.config import Config
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import default_menu_items
from compas_viewer.uidefinitions import default_toolbar_items


def _toolbar(monkeypatch, config=None, items=None):
    app = QApplication.instance() or QApplication([])
    config = config or Config()
    state = ViewerState(config)
    render_command = Mock(side_effect=lambda *, mode: state.set("renderer.rendermode", mode))
    view_command = Mock(side_effect=lambda *, mode: state.set("renderer.view", mode))
    viewer = SimpleNamespace(
        toolbar_items=default_toolbar_items() if items is None else items,
        state=state,
        commands={
            "viewer.change_rendermode": render_command,
            "viewer.change_view": view_command,
        },
    )
    monkeypatch.setattr(ToolBar, "viewer", property(lambda _self: viewer), raising=False)
    window = QMainWindow()
    toolbar = ToolBar(SimpleNamespace(widget=window))
    return toolbar, viewer, render_command, view_command, app, window


def test_default_toolbar_declares_render_mode_and_view_selectors():
    items = default_toolbar_items()

    assert [item["title"] for item in items] == ["Render Mode", "View"]
    assert [item["type"] for item in items] == ["select", "select"]
    assert items[0]["state"] == "renderer.rendermode"
    assert [(item["title"], item["value"]) for item in items[0]["items"]] == [
        ("Shaded", "shaded"),
        ("Ghosted", "ghosted"),
        ("Lighted", "lighted"),
        ("Wireframe", "wireframe"),
    ]
    assert items[1]["state"] == "renderer.view"
    assert [(item["title"], item["value"]) for item in items[1]["items"]] == [
        ("Perspective", "perspective"),
        ("Top", "top"),
        ("Front", "front"),
        ("Right", "right"),
        ("Ortho", "ortho"),
    ]


def test_toolbar_selectors_initialize_from_configured_renderer_state(monkeypatch):
    config = Config()
    config.renderer.rendermode = "wireframe"
    config.renderer.view = "top"
    toolbar, _viewer, _render_command, _view_command, app, window = _toolbar(monkeypatch, config=config)

    render_selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_rendermode")
    view_selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_view")

    assert render_selector.currentData() == "wireframe"
    assert view_selector.currentData() == "top"
    assert app is not None
    window.close()


def test_toolbar_selection_invokes_existing_command_once(monkeypatch):
    toolbar, viewer, render_command, view_command, _app, window = _toolbar(monkeypatch)
    render_selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_rendermode")
    view_selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_view")

    render_selector.setCurrentText("Wireframe")
    view_selector.setCurrentText("Front")

    render_command.assert_called_once_with(mode="wireframe")
    view_command.assert_called_once_with(mode="front")
    assert viewer.state.get("renderer.rendermode") == "wireframe"
    assert viewer.state.get("renderer.view") == "front"
    window.close()


def test_state_updates_toolbar_without_reinvoking_commands(monkeypatch):
    toolbar, viewer, render_command, view_command, _app, window = _toolbar(monkeypatch)
    render_selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_rendermode")
    view_selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_view")

    viewer.state.set("renderer.rendermode", "ghosted")
    viewer.state.set("renderer.view", "ortho")

    assert render_selector.currentData() == "ghosted"
    assert view_selector.currentData() == "ortho"
    render_command.assert_not_called()
    view_command.assert_not_called()
    window.close()


def test_toolbar_menu_and_display_form_share_one_state_path(monkeypatch):
    class Renderer:
        def __init__(self, state):
            self.state = state
            self._rendermode = state.get("renderer.rendermode")
            self._view = state.get("renderer.view")

        @property
        def rendermode(self):
            return self._rendermode

        @rendermode.setter
        def rendermode(self, value):
            self._rendermode = value
            self.state.set("renderer.rendermode", value)

        @property
        def view(self):
            return self._view

        @view.setter
        def view(self, value):
            self._view = value
            self.state.set("renderer.view", value)

    class Command:
        keybinding = None

        def __init__(self, callback):
            self.callback = Mock(side_effect=callback)

        def __call__(self, **kwargs):
            return self.callback(**kwargs)

    app = QApplication.instance() or QApplication([])
    config = Config()
    state = ViewerState(config)
    renderer = Renderer(state)
    render_command = Command(lambda *, mode: setattr(renderer, "rendermode", mode))
    view_command = Command(lambda *, mode: setattr(renderer, "view", mode))
    view_menu = next(item for item in default_menu_items() if item.get("title") == "View")
    groups = [item for item in view_menu["items"] if item.get("title") in {"Set Render Mode", "Set Current View"}]
    viewer = SimpleNamespace(
        app=app,
        config=config,
        state=state,
        toolbar_items=default_toolbar_items(),
        menu_items=[{"title": "View", "items": groups}],
        commands={
            "viewer.change_rendermode": render_command,
            "viewer.change_view": view_command,
        },
    )
    monkeypatch.setattr(ToolBar, "viewer", property(lambda _self: viewer), raising=False)
    monkeypatch.setattr(MenuBar, "viewer", property(lambda _self: viewer), raising=False)
    monkeypatch.setattr(DisplaySetting, "viewer", property(lambda _self: viewer), raising=False)
    window = QMainWindow()
    owner = SimpleNamespace(widget=window)
    menubar = MenuBar(owner)
    toolbar = ToolBar(owner)
    display = DisplaySetting(SimpleNamespace(renderer=renderer))
    render_selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_rendermode")
    display_selector = display._state_controls["renderer.rendermode"].combobox
    render_menu = next(menu for menu in menubar._menus if menu.title() == "Set Render Mode")
    render_actions = {action.text(): action for action in render_menu.actions()}

    render_selector.setCurrentText("Wireframe")

    assert state.get("renderer.rendermode") == "wireframe"
    assert display_selector.currentText() == "wireframe"
    assert render_actions["Wireframe"].isChecked()
    render_command.callback.assert_called_once_with(mode="wireframe")

    state.set("renderer.rendermode", "ghosted")

    assert render_selector.currentData() == "ghosted"
    assert display_selector.currentText() == "ghosted"
    assert render_actions["Ghosted"].isChecked()
    render_command.callback.assert_called_once_with(mode="wireframe")

    app.removeEventFilter(menubar._escape_filter)
    window.close()


@pytest.mark.parametrize(
    "items, message",
    [
        ([{"type": "select", "state": "renderer.view", "items": [{"title": "Top", "command": "viewer.change_view", "value": "top"}]}], "title"),
        ([{"title": "View", "type": "select", "items": [{"title": "Top", "command": "viewer.change_view", "value": "top"}]}], "state path"),
        ([{"title": "View", "type": "select", "state": "renderer.view", "items": []}], "at least one option"),
        ([{"title": "View", "type": "select", "state": "renderer.view", "items": [{"title": "Top", "command": "viewer.change_view"}]}], "state value"),
    ],
)
def test_invalid_toolbar_selectors_fail_clearly(monkeypatch, items, message):
    with pytest.raises(ValueError, match=message):
        _toolbar(monkeypatch, items=items)


def test_toolbar_rejects_unsupported_current_state(monkeypatch):
    config = Config()
    config.renderer.view = "other"

    with pytest.raises(ValueError, match="does not support state value 'other'"):
        _toolbar(monkeypatch, config=config)
