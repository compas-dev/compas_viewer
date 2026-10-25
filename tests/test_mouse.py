from types import SimpleNamespace

from PySide6.QtCore import QEvent
from PySide6.QtCore import QPoint

from compas_viewer.commands import rotate_view
from compas_viewer.mouse import Mouse


def test_click_jitter_does_not_start_a_drag():
    mouse = Mouse()
    mouse.begin(QPoint(100, 100))
    mouse.pos = QPoint(101, 101)

    assert not mouse.has_dragged()


def test_pointer_movement_crossing_threshold_starts_a_drag():
    mouse = Mouse()
    mouse.begin(QPoint(100, 100))
    mouse.pos = QPoint(103, 100)

    assert mouse.has_dragged()


def test_releasing_pointer_clears_drag_state():
    mouse = Mouse()
    mouse.begin(QPoint(100, 100))
    mouse.pos = QPoint(110, 100)
    mouse.end(QPoint(110, 100))

    assert not mouse.has_dragged()
    assert mouse.dx() == 0
    assert mouse.dy() == 0


def test_rotation_ignores_pointer_jitter_below_drag_threshold():
    rotations = []
    mouse = Mouse()
    mouse.begin(QPoint(100, 100))
    mouse.pos = QPoint(101, 101)
    camera = SimpleNamespace(rotate=lambda dx, dy: rotations.append((dx, dy)))
    viewer = SimpleNamespace(mouse=mouse, renderer=SimpleNamespace(camera=camera, update=lambda: None))
    event = SimpleNamespace(type=lambda: QEvent.Type.MouseMove)

    rotate_view(viewer, event)

    assert rotations == []
