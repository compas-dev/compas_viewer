from types import SimpleNamespace
from unittest.mock import Mock

from PySide6.QtCore import QPoint
from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt

from compas_viewer.events import EventManager


class MouseEvent:
    def __init__(self, buttons, x=10, y=20):
        self._buttons = buttons
        self._point = QPoint(x, y)
        self._pointf = QPointF(x, y)

    def buttons(self):
        return self._buttons

    def pos(self):
        return self._point

    def position(self):
        return self._pointf


class KeyEvent:
    def __init__(self, key, modifiers=Qt.KeyboardModifier.NoModifier):
        self._key = key
        self._modifiers = modifiers

    def key(self):
        return self._key

    def modifiers(self):
        return self._modifiers


class Binding:
    def __init__(self, button="LEFT"):
        self.button = button
        self.triggered = SimpleNamespace(emit=Mock())
        self.is_active = False

    def __eq__(self, event):
        return True


def manager_for(monkeypatch, viewer):
    monkeypatch.setattr(EventManager, "viewer", property(lambda _self: viewer))
    manager = object.__new__(EventManager)
    manager.key_events = []
    manager.mouse_events = []
    manager.wheel_events = []
    return manager


def viewer_stub(*, active=True, cancel=True):
    return SimpleNamespace(
        cancel_measurement=Mock(return_value=cancel),
        _accept_measurement_at=Mock(),
        _update_measurement_hover=Mock(),
        state=SimpleNamespace(measurement=SimpleNamespace(active=active)),
        mouse=SimpleNamespace(begin=Mock(), pos=QPoint(), last_pos=QPoint(), end=Mock()),
    )


def test_escape_cancels_measurement_before_deselection(monkeypatch):
    viewer = viewer_stub(cancel=True)
    manager = manager_for(monkeypatch, viewer)
    deselect = Binding()
    manager.key_events = [deselect]  # type: ignore[list-item]

    manager.delegate_keypress(KeyEvent(Qt.Key.Key_Escape))

    viewer.cancel_measurement.assert_called_once_with()
    deselect.triggered.emit.assert_not_called()


def test_escape_dispatches_normally_without_measurement_state(monkeypatch):
    viewer = viewer_stub(cancel=False)
    manager = manager_for(monkeypatch, viewer)
    deselect = Binding()
    manager.key_events = [deselect]  # type: ignore[list-item]

    manager.delegate_keypress(KeyEvent(Qt.Key.Key_Escape))

    deselect.triggered.emit.assert_called_once_with()


def test_active_measurement_consumes_left_press_before_selection(monkeypatch):
    viewer = viewer_stub(active=True)
    manager = manager_for(monkeypatch, viewer)
    selection = Binding("LEFT")
    manager.mouse_events = [selection]  # type: ignore[list-item]
    event = MouseEvent(Qt.MouseButton.LeftButton)

    manager.delegate_mousepress(event)

    viewer.mouse.begin.assert_called_once_with(event.pos())
    viewer._accept_measurement_at.assert_called_once_with((10.0, 20.0))
    selection.triggered.emit.assert_not_called()
    assert not selection.is_active


def test_active_measurement_hover_skips_left_bindings(monkeypatch):
    viewer = viewer_stub(active=True)
    manager = manager_for(monkeypatch, viewer)
    selection = Binding("LEFT")
    manager.mouse_events = [selection]  # type: ignore[list-item]
    event = MouseEvent(Qt.MouseButton.LeftButton)

    manager.delegate_mousemove(event)

    viewer._update_measurement_hover.assert_called_once_with((10.0, 20.0))
    selection.triggered.emit.assert_not_called()
    assert viewer.mouse.last_pos == event.pos()


def test_background_hover_queries_without_buttons(monkeypatch):
    viewer = viewer_stub(active=True)
    manager = manager_for(monkeypatch, viewer)
    event = MouseEvent(Qt.MouseButton.NoButton)

    manager.delegate_mousemove(event)

    viewer._update_measurement_hover.assert_called_once_with((10.0, 20.0))


def test_right_button_navigation_skips_hover_and_dispatches_binding(monkeypatch):
    viewer = viewer_stub(active=True)
    manager = manager_for(monkeypatch, viewer)
    rotate = Binding("RIGHT")
    manager.mouse_events = [rotate]  # type: ignore[list-item]
    event = MouseEvent(Qt.MouseButton.RightButton)

    manager.delegate_mousemove(event)

    viewer._update_measurement_hover.assert_not_called()
    rotate.triggered.emit.assert_called_once_with(event)


def test_wheel_navigation_remains_available_during_measurement(monkeypatch):
    viewer = viewer_stub(active=True)
    manager = manager_for(monkeypatch, viewer)
    zoom = Binding()
    manager.wheel_events = [zoom]  # type: ignore[list-item]
    event = object()

    manager.delegate_wheel(event)  # type: ignore[arg-type]

    zoom.triggered.emit.assert_called_once_with(event)


def test_inactive_measurement_preserves_normal_left_dispatch(monkeypatch):
    viewer = viewer_stub(active=False)
    manager = manager_for(monkeypatch, viewer)
    selection = Binding("LEFT")
    manager.mouse_events = [selection]  # type: ignore[list-item]
    event = MouseEvent(Qt.MouseButton.LeftButton)

    manager.delegate_mousepress(event)

    viewer._accept_measurement_at.assert_not_called()
    selection.triggered.emit.assert_called_once_with(event)
    assert selection.is_active
