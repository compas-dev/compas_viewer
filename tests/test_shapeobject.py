from unittest.mock import Mock

from compas.geometry import Sphere
from compas_viewer import Viewer


def test_shape_object_preserves_geometry_resolution(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    viewer = Viewer()
    shape = Sphere(1.0)
    shape.resolution_u = 24
    shape.resolution_v = 12

    sceneobject = viewer.scene.add(shape)

    assert sceneobject.u == 24
    assert sceneobject.v == 12


def test_shape_object_resolution_override(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    viewer = Viewer()
    shape = Sphere(1.0)

    sceneobject = viewer.scene.add(shape, u=24, v=12)

    assert sceneobject.u == 24
    assert sceneobject.v == 12


def test_changing_shape_object_resolution_rebuilds_buffers(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    viewer = Viewer()
    sceneobject = viewer.scene.add(Sphere(1.0))
    rebuild_buffers = Mock()
    update = Mock()
    monkeypatch.setattr(viewer.renderer, "rebuild_buffers", rebuild_buffers)
    monkeypatch.setattr(viewer.renderer, "update", update)
    viewer.running = True

    try:
        sceneobject.u = 24
    finally:
        viewer.running = False

    assert sceneobject.geometry.resolution_u == 24
    rebuild_buffers.assert_called_once_with()
    update.assert_called_once_with()
