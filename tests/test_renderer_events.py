from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from compas_viewer.renderer import Renderer


@pytest.mark.parametrize(
    ("handler", "delegate"),
    [
        ("mouseMoveEvent", "delegate_mousemove"),
        ("mousePressEvent", "delegate_mousepress"),
        ("mouseReleaseEvent", "delegate_mouserelease"),
        ("wheelEvent", "delegate_wheel"),
    ],
)
def test_mouse_event_dispatch_uses_pointer_ownership_not_window_activation(handler, delegate):
    event = object()
    eventmanager = Mock()
    renderer = SimpleNamespace(
        viewer=SimpleNamespace(eventmanager=eventmanager),
        underMouse=Mock(return_value=True),
        isActiveWindow=Mock(return_value=False),
    )

    getattr(Renderer, handler)(renderer, event)

    renderer.underMouse.assert_called_once_with()
    renderer.isActiveWindow.assert_not_called()
    getattr(eventmanager, delegate).assert_called_once_with(event)


@pytest.mark.parametrize(
    ("handler", "delegate"),
    [
        ("mouseMoveEvent", "delegate_mousemove"),
        ("mousePressEvent", "delegate_mousepress"),
        ("mouseReleaseEvent", "delegate_mouserelease"),
        ("wheelEvent", "delegate_wheel"),
    ],
)
def test_mouse_event_dispatch_still_requires_pointer_ownership(handler, delegate):
    eventmanager = Mock()
    renderer = SimpleNamespace(
        viewer=SimpleNamespace(eventmanager=eventmanager),
        underMouse=Mock(return_value=False),
        isActiveWindow=Mock(return_value=True),
    )

    getattr(Renderer, handler)(renderer, object())

    renderer.underMouse.assert_called_once_with()
    renderer.isActiveWindow.assert_not_called()
    getattr(eventmanager, delegate).assert_not_called()
