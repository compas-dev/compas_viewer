from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QStyleOptionToolButton
from PySide6.QtWidgets import QToolButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from PySide6.QtTest import QTest
from PySide6.QtTest import QSignalSpy

from compas_viewer.components.viewport import _ViewControl
from compas_viewer._theme import application_palette
from compas_viewer.config import Config
from compas_viewer.state import ViewerState


def _control(monkeypatch):
    app = QApplication.instance() or QApplication([])
    app.setQuitOnLastWindowClosed(False)
    state = ViewerState(Config())
    renderer = QWidget()
    renderer.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    renderer.setFocus = Mock(wraps=renderer.setFocus)
    view_command = Mock(side_effect=lambda *, mode: state.set("renderer.view", mode))
    render_command = Mock(side_effect=lambda *, mode: state.set("renderer.rendermode", mode))
    viewer = SimpleNamespace(
        state=state,
        commands={"viewer.change_view": view_command, "viewer.change_rendermode": render_command},
    )
    monkeypatch.setattr(_ViewControl, "viewer", property(lambda _self: viewer), raising=False)
    window = QMainWindow()
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.addWidget(renderer)
    control = _ViewControl(renderer, container)
    layout.addWidget(control)
    window.setCentralWidget(container)
    return control, renderer, state, view_command, render_command, app, window


def _activate(window, app):
    window.show()
    window.windowHandle().requestActivate()
    window.activateWindow()
    assert QTest.qWaitForWindowActive(window, 1000)
    app.processEvents()
    assert QGuiApplication.focusWindow() is window.windowHandle()


def test_view_control_exposes_grouped_semantic_choices(monkeypatch):
    control, _renderer, state, view_command, render_command, _app, window = _control(monkeypatch)
    button = control.findChild(QToolButton, "viewport_view_menu_button")
    menu = button.menu()

    assert button.text() == "View / View Mode"
    assert button.accessibleName() == "View and View Mode"
    assert button.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert [(action.text(), action.isEnabled()) for action in menu.actions() if not action.isSeparator()] == [
        ("View", False),
        ("Perspective", True),
        ("Top", True),
        ("Front", True),
        ("Right", True),
        ("Ortho", True),
        ("View Mode", False),
        ("Shaded", True),
        ("Lighted", True),
        ("Ghosted", True),
        ("Wireframe", True),
    ]
    assert control._actions["renderer.view"]["perspective"].isChecked()
    assert control._actions["renderer.rendermode"]["shaded"].isChecked()
    assert state.get("renderer.view") == "perspective"
    view_command.assert_not_called()
    render_command.assert_not_called()
    window.close()


@pytest.mark.parametrize("appearance", ["light", "dark"])
@pytest.mark.parametrize("font_scale", [1.0, 1.5])
def test_view_menu_button_accommodates_label_and_native_indicator_in_one_row(monkeypatch, appearance, font_scale):
    app = QApplication.instance() or QApplication([])
    original_palette = app.palette()
    original_font = app.font()
    scaled_font = QFont(original_font)
    scaled_font.setPointSizeF(original_font.pointSizeF() * font_scale)
    app.setPalette(application_palette(appearance))
    app.setFont(scaled_font)
    try:
        control, _renderer, _state, _view_command, _render_command, app, window = _control(monkeypatch)
        _activate(window, app)
        button = control._button
        button.ensurePolished()
        control.adjustSize()
        app.processEvents()

        text_rect, indicator_rect = button._presentation_rects()
        label_bounds = button.fontMetrics().boundingRect(text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextSingleLine, button.text())
        frame_option = button._frame_option()

        assert button.minimumWidth() <= button.width()
        assert text_rect.contains(label_bounds)
        assert text_rect.right() < indicator_rect.left()
        assert abs(label_bounds.center().y() - indicator_rect.center().y()) <= 1
        assert button.sizeHint().height() < 2 * button.fontMetrics().lineSpacing()
        assert not frame_option.features & QStyleOptionToolButton.ToolButtonFeature.HasMenu
        assert not frame_option.features & QStyleOptionToolButton.ToolButtonFeature.Menu
        window.close()
    finally:
        app.setFont(original_font)
        app.setPalette(original_palette)


def test_view_menu_label_and_arrow_geometry_is_stable_across_interaction_states(monkeypatch):
    control, _renderer, _state, _view_command, _render_command, app, window = _control(monkeypatch)
    _activate(window, app)
    button = control._button
    menu = control._menu
    button.ensurePolished()
    control.adjustSize()
    app.processEvents()

    def snapshot():
        text_rect, indicator_rect = button._presentation_rects()
        return text_rect, indicator_rect, button.grab().size()

    normal = snapshot()
    QTest.mouseMove(button, button.rect().center())
    app.processEvents()
    hovered = snapshot()
    button.setDown(True)
    app.processEvents()
    pressed = snapshot()
    menu.popup(button.mapToGlobal(button.rect().bottomLeft()))
    app.processEvents()
    menu_open = snapshot()
    menu.hide()
    button.setDown(False)
    app.processEvents()
    released = snapshot()

    assert hovered == normal
    assert pressed == normal
    assert menu_open == normal
    assert released == normal
    window.close()


def test_view_control_invokes_command_once_and_restores_renderer_focus(monkeypatch):
    control, renderer, state, view_command, render_command, app, window = _control(monkeypatch)
    menu = control._menu

    _activate(window, app)
    menu.popup(control.mapToGlobal(control.rect().bottomLeft()))
    app.processEvents()
    control._actions["renderer.view"]["front"].trigger()
    menu.hide()
    app.processEvents()

    view_command.assert_called_once_with(mode="front")
    render_command.assert_not_called()
    assert state.get("renderer.view") == "front"
    assert control._actions["renderer.view"]["front"].isChecked()
    renderer.setFocus.assert_called_once_with(Qt.FocusReason.OtherFocusReason)
    assert QApplication.focusWidget() is renderer
    assert control._focus_pending is False
    assert control._focus_listener_connected is False
    window.close()


def test_keyboard_selection_invokes_once_and_restores_renderer_focus(monkeypatch):
    control, renderer, state, view_command, render_command, app, window = _control(monkeypatch)
    button = control._button
    menu = control._menu
    _activate(window, app)
    button.setFocus()

    QTest.keyClick(button, Qt.Key.Key_Space)
    app.processEvents()
    assert menu.isVisible()
    menu.setActiveAction(control._actions["renderer.rendermode"]["wireframe"])
    QTest.keyClick(menu, Qt.Key.Key_Return)
    app.processEvents()

    render_command.assert_called_once_with(mode="wireframe")
    view_command.assert_not_called()
    assert state.get("renderer.rendermode") == "wireframe"
    renderer.setFocus.assert_called_once_with(Qt.FocusReason.OtherFocusReason)
    assert QApplication.focusWidget() is renderer
    assert control._focus_pending is False
    assert control._focus_listener_connected is False
    window.close()


def test_keyboard_escape_cancels_without_command_and_restores_renderer_focus(monkeypatch):
    control, renderer, _state, view_command, render_command, app, window = _control(monkeypatch)
    button = control._button
    menu = control._menu
    cancelled = QSignalSpy(menu.cancelled)
    _activate(window, app)
    button.setFocus()

    QTest.keyClick(button, Qt.Key.Key_Space)
    app.processEvents()
    assert menu.isVisible()
    QTest.keyClick(menu, Qt.Key.Key_Escape)
    app.processEvents()

    assert cancelled.count() == 1
    assert not menu.isVisible()
    view_command.assert_not_called()
    render_command.assert_not_called()
    assert control._focus_pending is False, (
        control._menu.isVisible(),
        window.isActiveWindow(),
        QGuiApplication.focusWindow() is window.windowHandle(),
        control._focus_listener_connected,
    )
    renderer.setFocus.assert_called_once_with(Qt.FocusReason.OtherFocusReason)
    assert QApplication.focusWidget() is renderer
    assert control._focus_pending is False
    assert control._focus_listener_connected is False
    window.close()


def test_view_control_tracks_state_without_reinvoking_command(monkeypatch):
    control, _renderer, state, view_command, render_command, _app, window = _control(monkeypatch)

    state.set("renderer.view", "ortho")
    state.set("renderer.rendermode", "wireframe")

    assert control._actions["renderer.view"]["ortho"].isChecked()
    assert control._actions["renderer.rendermode"]["wireframe"].isChecked()
    assert sum(action.isChecked() for action in control._actions["renderer.view"].values()) == 1
    assert sum(action.isChecked() for action in control._actions["renderer.rendermode"].values()) == 1
    view_command.assert_not_called()
    render_command.assert_not_called()
    window.close()
