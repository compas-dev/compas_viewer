from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from compas.colors import Color
from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QWidget
from PySide6.QtTest import QSignalSpy
from PySide6.QtTest import QTest

from compas_viewer.components.displaysetting import DisplaySetting
from compas_viewer.components.menubar import MenuBar
from compas_viewer.components.toolbar import ToolBar
from compas_viewer.commands import capture_view
from compas_viewer.config import Config
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import default_menu_items
from compas_viewer.uidefinitions import default_toolbar_items


class FocusProbe(QWidget):
    def __init__(self):
        super().__init__()
        self.focus_in_reasons = []
        self.set_focus_reasons = []
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def focusInEvent(self, event: QFocusEvent):  # noqa: N802
        self.focus_in_reasons.append(event.reason())
        super().focusInEvent(event)

    def setFocus(self, reason=Qt.FocusReason.OtherFocusReason):  # noqa: N802
        self.set_focus_reasons.append(reason)
        super().setFocus(reason)


def _toolbar(monkeypatch, config=None, items=None, *, actual_renderer=False):
    app = QApplication.instance() or QApplication([])
    config = config or Config()
    state = ViewerState(config)
    render_command = Mock(side_effect=lambda *, mode: state.set("renderer.rendermode", mode))
    view_command = Mock(side_effect=lambda *, mode: state.set("renderer.view", mode))
    renderer = FocusProbe() if actual_renderer else Mock()
    viewer = SimpleNamespace(
        toolbar_items=default_toolbar_items() if items is None else items,
        state=state,
        renderer=renderer,
        commands={
            "viewer.change_rendermode": render_command,
            "viewer.change_view": view_command,
            "viewer.zoom_selected": Mock(),
            "viewer.zoom_extents": Mock(),
            "viewer.capture_view": Mock(),
            "viewer.inspect_distance": Mock(),
            "viewer.add_fixed_distance_dimension": Mock(),
            "viewer.add_associative_distance_dimension": Mock(),
            "viewer.cancel_measurement": Mock(),
        },
    )
    monkeypatch.setattr(ToolBar, "viewer", property(lambda _self: viewer), raising=False)
    window = QMainWindow()
    if actual_renderer:
        window.setCentralWidget(renderer)
    window.activateWindow = Mock(wraps=window.activateWindow)
    toolbar = ToolBar(SimpleNamespace(widget=window))
    return toolbar, viewer, render_command, view_command, app, window


def _activate(window, app):
    window.show()
    window.windowHandle().requestActivate()
    window.activateWindow()
    assert QTest.qWaitForWindowActive(window, 1000)
    app.processEvents()
    assert QGuiApplication.focusWindow() is window.windowHandle()
    assert window.isActiveWindow()
    window.activateWindow.reset_mock()


def _render_selector_items():
    options = []
    for mode in ("shaded", "ghosted", "lighted", "wireframe"):
        options.append({"title": mode.title(), "command": "viewer.change_rendermode", "value": mode, "kwargs": {"mode": mode}})
    return [
        {
            "title": "Render Mode",
            "type": "select",
            "state": "renderer.rendermode",
            "items": options,
        }
    ]


def _render_button_items():
    return [
        {
            "title": mode.title(),
            "type": "button",
            "command": "viewer.change_rendermode",
            "state": "renderer.rendermode",
            "value": mode,
            "kwargs": {"mode": mode},
        }
        for mode in ("shaded", "lighted", "ghosted", "wireframe")
    ]


def test_default_toolbar_declares_utility_and_measurement_buttons():
    items = default_toolbar_items()

    assert [item["title"] for item in items] == ["Zoom Selected", "Zoom Extents", "Capture View", "Measurement"]
    assert [item["type"] for item in items] == ["button", "button", "button", "menu_button"]
    assert [item["icon"] for item in items] == [
        "zoom_selected.svg",
        "zoom_extents.svg",
        "capture_view.svg",
        "measurement.svg",
    ]
    assert all(item["icon_only"] is True for item in items)
    assert [option["command"] for option in items[-1]["items"]] == [
        "viewer.inspect_distance",
        "viewer.add_fixed_distance_dimension",
        "viewer.add_associative_distance_dimension",
        "viewer.cancel_measurement",
    ]


def test_toolbar_utility_buttons_invoke_existing_commands_once(monkeypatch):
    toolbar, viewer, _render_command, _view_command, app, window = _toolbar(monkeypatch)
    _activate(window, app)

    for title, command_id in (
        ("Zoom Selected", "viewer.zoom_selected"),
        ("Zoom Extents", "viewer.zoom_extents"),
        ("Capture View", "viewer.capture_view"),
    ):
        button = next(
            toolbar.widget.widgetForAction(action)
            for action in toolbar.widget.actions()
            if isinstance(toolbar.widget.widgetForAction(action), QPushButton) and toolbar.widget.widgetForAction(action).accessibleName() == title
        )
        assert button.text() == ""
        assert button.toolTip() == title
        assert not button.icon().isNull()
        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
        viewer.commands[command_id].assert_called_once_with()
        app.processEvents()
        viewer.renderer.setFocus.assert_called_once_with(Qt.FocusReason.OtherFocusReason)
        viewer.renderer.setFocus.reset_mock()
        window.activateWindow.reset_mock()

    window.close()


def test_measurement_menu_invokes_existing_commands_and_restores_focus(monkeypatch):
    toolbar, viewer, _render_command, _view_command, app, window = _toolbar(monkeypatch)
    button = toolbar.widget.findChild(QPushButton, "toolbar_menu_measurement")
    menu = button.menu()
    _activate(window, app)

    assert button.text() == ""
    assert button.toolTip() == "Measurement"
    assert button.accessibleName() == "Measurement"
    assert not button.icon().isNull()
    assert [action.text() for action in menu.actions()] == [
        "Inspect Distance",
        "Add Fixed Distance Dimension",
        "Add Associative Distance Dimension",
        "Cancel Measurement",
    ]

    for action, command_id in zip(
        menu.actions(),
        (
            "viewer.inspect_distance",
            "viewer.add_fixed_distance_dimension",
            "viewer.add_associative_distance_dimension",
            "viewer.cancel_measurement",
        ),
        strict=True,
    ):
        menu.popup(window.mapToGlobal(window.rect().center()))
        app.processEvents()
        action.trigger()
        menu.hide()
        app.processEvents()
        viewer.commands[command_id].assert_called_once_with()
        viewer.renderer.setFocus.assert_called_once_with(Qt.FocusReason.OtherFocusReason)
        viewer.renderer.setFocus.reset_mock()
        window.activateWindow.reset_mock()

    window.close()


def test_cancelled_capture_returns_focus_without_saving(monkeypatch):
    toolbar, viewer, _render_command, _view_command, app, window = _toolbar(monkeypatch)
    capture_owner = SimpleNamespace(
        ui=SimpleNamespace(window=SimpleNamespace(widget=window)),
        save_image=Mock(),
    )
    monkeypatch.setattr(QFileDialog, "getSaveFileName", Mock(return_value=("", "Images (*.png *.jpg)")))
    capture_command = viewer.commands["viewer.capture_view"]
    capture_command.side_effect = lambda: capture_view(capture_owner)
    capture = next(
        toolbar.widget.widgetForAction(action)
        for action in toolbar.widget.actions()
        if isinstance(toolbar.widget.widgetForAction(action), QPushButton) and toolbar.widget.widgetForAction(action).accessibleName() == "Capture View"
    )
    _activate(window, app)

    QTest.mouseClick(capture, Qt.MouseButton.LeftButton)
    app.processEvents()

    capture_command.assert_called_once_with()
    capture_owner.save_image.assert_not_called()
    viewer.renderer.setFocus.assert_called_once_with(Qt.FocusReason.OtherFocusReason)
    window.close()


def test_mouse_popup_selection_restores_focus_once_after_real_teardown(monkeypatch):
    toolbar, viewer, render_command, _view_command, app, window = _toolbar(monkeypatch, items=_render_selector_items(), actual_renderer=True)
    selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_rendermode")
    _activate(window, app)
    selector.setFocus()
    app.processEvents()
    viewer.renderer.focus_in_reasons.clear()
    selector.showPopup()
    app.processEvents()
    assert selector.view().isVisible()
    hidden = QSignalSpy(selector.popup_hidden)

    index = selector.model().index(3, 0)
    QTest.mouseClick(selector.view().viewport(), Qt.MouseButton.LeftButton, pos=selector.view().visualRect(index).center())
    if selector.view().isVisible():
        selector.hidePopup()
    if hidden.count() == 0:
        assert hidden.wait(1000)
    app.processEvents()

    assert hidden.count() == 1
    render_command.assert_called_once_with(mode="wireframe")
    window.activateWindow.assert_called_once_with()
    assert QApplication.focusWidget() is viewer.renderer
    assert viewer.renderer.focus_in_reasons == [Qt.FocusReason.OtherFocusReason]
    assert selector.focusPolicy() != Qt.FocusPolicy.NoFocus
    window.close()


def test_keyboard_return_popup_selection_restores_focus_once(monkeypatch):
    toolbar, viewer, render_command, _view_command, app, window = _toolbar(monkeypatch, items=_render_selector_items(), actual_renderer=True)
    selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_rendermode")
    _activate(window, app)
    selector.setFocus()
    app.processEvents()
    viewer.renderer.focus_in_reasons.clear()
    selector.showPopup()
    app.processEvents()
    assert selector.view().isVisible()
    hidden = QSignalSpy(selector.popup_hidden)

    selector.view().setCurrentIndex(selector.model().index(2, 0))
    QTest.keyClick(selector.view(), Qt.Key.Key_Return)
    if selector.view().isVisible():
        selector.hidePopup()
    if hidden.count() == 0:
        assert hidden.wait(1000)
    app.processEvents()

    assert hidden.count() == 1
    render_command.assert_called_once_with(mode="lighted")
    window.activateWindow.assert_called_once_with()
    assert QApplication.focusWidget() is viewer.renderer
    assert viewer.renderer.focus_in_reasons == [Qt.FocusReason.OtherFocusReason]
    assert selector.focusPolicy() != Qt.FocusPolicy.NoFocus
    window.close()


def test_escape_cancelled_popup_restores_focus_without_invoking_command(monkeypatch):
    toolbar, viewer, render_command, view_command, app, window = _toolbar(monkeypatch, items=_render_selector_items(), actual_renderer=True)
    selector = toolbar.widget.findChild(QComboBox, "toolbar_renderer_rendermode")
    _activate(window, app)
    selector.setFocus()
    app.processEvents()
    viewer.renderer.focus_in_reasons.clear()
    selector.showPopup()
    app.processEvents()
    assert selector.view().isVisible()
    hidden = QSignalSpy(selector.popup_hidden)

    QTest.keyClick(selector.view(), Qt.Key.Key_Escape)
    if selector.view().isVisible():
        selector.hidePopup()
    if hidden.count() == 0:
        assert hidden.wait(1000)
    app.processEvents()

    assert hidden.count() == 1
    render_command.assert_not_called()
    view_command.assert_not_called()
    window.activateWindow.assert_called_once_with()
    assert QApplication.focusWidget() is viewer.renderer
    assert viewer.renderer.focus_in_reasons == [Qt.FocusReason.OtherFocusReason]
    assert selector.focusPolicy() != Qt.FocusPolicy.NoFocus
    window.close()


def test_pending_focus_request_completes_on_main_focus_window_change(monkeypatch):
    toolbar, viewer, _render_command, _view_command, app, window = _toolbar(monkeypatch, actual_renderer=True)
    _activate(window, app)
    other = QMainWindow()
    other.show()
    other.windowHandle().requestActivate()
    other.activateWindow()
    assert QTest.qWaitForWindowActive(other, 1000)
    app.processEvents()
    assert QGuiApplication.focusWindow() is other.windowHandle()
    viewer.renderer.set_focus_reasons.clear()

    with monkeypatch.context() as activation_patch:
        activation_patch.setattr(window.windowHandle(), "requestActivate", Mock())
        activation_patch.setattr(window, "activateWindow", Mock())
        toolbar._focus_restorer.request()
        app.processEvents()

        assert toolbar._focus_restorer._pending is True
        assert QGuiApplication.focusWindow() is other.windowHandle()
        assert viewer.renderer.set_focus_reasons == []

    window.activateWindow()
    assert QTest.qWaitForWindowActive(window, 1000)
    app.processEvents()

    assert QGuiApplication.focusWindow() is window.windowHandle()
    assert toolbar._focus_restorer._pending is False
    assert QApplication.focusWidget() is viewer.renderer
    assert viewer.renderer.set_focus_reasons == [Qt.FocusReason.OtherFocusReason]
    other.close()
    window.close()


def test_state_updates_toolbar_without_reinvoking_commands(monkeypatch):
    toolbar, viewer, render_command, view_command, app, window = _toolbar(monkeypatch, items=_render_button_items())
    ghosted = toolbar.widget.findChild(QPushButton, "toolbar_renderer_rendermode_ghosted")

    viewer.state.set("renderer.rendermode", "ghosted")
    viewer.state.set("renderer.view", "ortho")

    assert ghosted.isChecked()
    assert sum(button.isChecked() for button, _value in toolbar._state_buttons["renderer.rendermode"]) == 1
    render_command.assert_not_called()
    view_command.assert_not_called()
    app.processEvents()
    window.activateWindow.assert_not_called()
    viewer.renderer.setFocus.assert_not_called()
    window.close()


def test_unsupported_state_clears_exclusive_buttons_until_supported_state_returns(monkeypatch):
    toolbar, viewer, _render_command, view_command, _app, window = _toolbar(monkeypatch, items=_render_button_items())
    buttons = toolbar._state_buttons["renderer.rendermode"]
    group = toolbar._state_button_groups["renderer.rendermode"]

    viewer.state.set("renderer.rendermode", "unsupported")

    assert group.exclusive()
    assert not any(button.isChecked() for button, _value in buttons)
    view_command.assert_not_called()

    viewer.state.set("renderer.rendermode", "lighted")

    assert group.exclusive()
    assert [(value, button.isChecked()) for button, value in buttons] == [
        ("shaded", False),
        ("lighted", True),
        ("ghosted", False),
        ("wireframe", False),
    ]
    view_command.assert_not_called()
    window.close()


def test_custom_toolbar_buttons_preserve_existing_unbound_schema(monkeypatch):
    items = [{"title": "Front", "type": "button", "command": "viewer.change_view", "kwargs": {"mode": "front"}}]
    toolbar, _viewer, _render_command, view_command, _app, window = _toolbar(monkeypatch, items=items)
    button = toolbar.widget.widgetForAction(toolbar.widget.actions()[0])
    assert isinstance(button, QPushButton)

    QTest.mouseClick(button, Qt.MouseButton.LeftButton)

    view_command.assert_called_once_with(mode="front")
    assert not button.isCheckable()
    window.close()


@pytest.mark.parametrize(
    ("icon", "expected_text"),
    [
        (None, "Custom"),
        ("view_top.svg", "Custom"),
    ],
)
def test_custom_state_buttons_preserve_text_with_optional_icon(monkeypatch, icon, expected_text):
    item = {
        "title": "Custom",
        "type": "button",
        "command": "viewer.change_view",
        "state": "renderer.view",
        "value": "top",
        "kwargs": {"mode": "top"},
    }
    if icon is not None:
        item["icon"] = icon
    toolbar, _viewer, _render_command, _view_command, _app, window = _toolbar(monkeypatch, items=[item])
    button = toolbar.widget.findChild(QPushButton, "toolbar_renderer_view_top")

    assert button.text() == expected_text
    assert button.icon().isNull() is (icon is None)
    assert button.toolTip() == "Custom"
    assert button.accessibleName() == "Custom"
    window.close()


def test_toolbar_menu_and_display_form_share_one_state_path(monkeypatch):
    class Renderer:
        def __init__(self, state):
            self.state = state
            self._rendermode = state.get("renderer.rendermode")
            self._view = state.get("renderer.view")
            self.backgroundcolor = config.renderer.backgroundcolor
            self.setFocus = Mock()

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
    config.renderer.backgroundcolor = Color.white()
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
        renderer=renderer,
        toolbar_items=_render_button_items(),
        menu_items=[{"title": "View", "items": groups}],
        commands={
            "viewer.change_rendermode": render_command,
            "viewer.change_view": view_command,
            "viewer.zoom_selected": Mock(),
            "viewer.zoom_extents": Mock(),
            "viewer.capture_view": Mock(),
            "viewer.inspect_distance": Mock(),
            "viewer.add_fixed_distance_dimension": Mock(),
            "viewer.add_associative_distance_dimension": Mock(),
            "viewer.cancel_measurement": Mock(),
        },
    )
    monkeypatch.setattr(ToolBar, "viewer", property(lambda _self: viewer), raising=False)
    monkeypatch.setattr(MenuBar, "viewer", property(lambda _self: viewer), raising=False)
    monkeypatch.setattr(DisplaySetting, "viewer", property(lambda _self: viewer), raising=False)
    window = QMainWindow()
    window.activateWindow = Mock(wraps=window.activateWindow)
    owner = SimpleNamespace(widget=window)
    menubar = MenuBar(owner)
    toolbar = ToolBar(owner)
    display = DisplaySetting(SimpleNamespace(renderer=renderer))
    _activate(window, app)
    wireframe_button = toolbar.widget.findChild(QPushButton, "toolbar_renderer_rendermode_wireframe")
    ghosted_button = toolbar.widget.findChild(QPushButton, "toolbar_renderer_rendermode_ghosted")
    display_selector = display._state_controls["renderer.rendermode"].combobox
    display_view = display._state_controls["renderer.view"].combobox
    render_menu = next(menu for menu in menubar._menus if menu.title() == "Set Render Mode")
    view_menu = next(menu for menu in menubar._menus if menu.title() == "Set Current View")
    render_actions = {action.text(): action for action in render_menu.actions()}
    view_actions = {action.text(): action for action in view_menu.actions()}

    QTest.mouseClick(wireframe_button, Qt.MouseButton.LeftButton)

    assert state.get("renderer.rendermode") == "wireframe"
    assert display_selector.currentText() == "wireframe"
    assert render_actions["Wireframe"].isChecked()
    render_command.callback.assert_called_once_with(mode="wireframe")
    app.processEvents()
    window.activateWindow.assert_called_once_with()
    renderer.setFocus.assert_called_once_with(Qt.FocusReason.OtherFocusReason)

    state.set("renderer.rendermode", "ghosted")

    assert ghosted_button.isChecked()
    assert display_selector.currentText() == "ghosted"
    assert render_actions["Ghosted"].isChecked()
    render_command.callback.assert_called_once_with(mode="wireframe")

    view_actions["Front"].trigger()

    assert state.get("renderer.view") == "front"
    assert display_view.currentText() == "front"
    view_command.callback.assert_called_once_with(mode="front")

    state.set("renderer.view", "ortho")

    assert display_view.currentText() == "ortho"
    view_command.callback.assert_called_once_with(mode="front")

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


@pytest.mark.parametrize(
    "items, message",
    [
        ([{"type": "menu_button", "items": [{"title": "Inspect", "command": "viewer.inspect_distance"}]}], "title"),
        ([{"title": "Measurement", "type": "menu_button", "items": []}], "at least one option"),
        ([{"title": "Measurement", "type": "menu_button", "items": [{"command": "viewer.inspect_distance"}]}], "without a title"),
        ([{"title": "Measurement", "type": "menu_button", "items": [{"title": "Inspect"}]}], "requires a command"),
    ],
)
def test_invalid_toolbar_menu_buttons_fail_clearly(monkeypatch, items, message):
    with pytest.raises(ValueError, match=message):
        _toolbar(monkeypatch, items=items)


def test_toolbar_leaves_buttons_unchecked_for_unsupported_current_state(monkeypatch):
    config = Config()
    config.renderer.rendermode = "other"

    toolbar, _viewer, _render_command, _view_command, _app, window = _toolbar(monkeypatch, config=config, items=_render_button_items())

    assert not any(button.isChecked() for button, _value in toolbar._state_buttons["renderer.rendermode"])
    window.close()


@pytest.mark.parametrize(
    ("item", "message"),
    [
        ({"type": "button", "command": "viewer.change_view", "state": "renderer.view", "value": "top"}, "title"),
        ({"title": "Top", "type": "button", "state": "renderer.view", "value": "top"}, "command"),
        ({"title": "Top", "type": "button", "command": "viewer.change_view", "state": "renderer.view"}, "state value"),
    ],
)
def test_invalid_state_bound_toolbar_buttons_fail_clearly(monkeypatch, item, message):
    with pytest.raises(ValueError, match=message):
        _toolbar(monkeypatch, items=[item])
