from compas.geometry import Circle
from compas.geometry import Ellipse
from compas_viewer import Viewer


def test_circle_object_uses_default_discretization(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    sceneobject = Viewer().scene.add(Circle(1.0))

    assert sceneobject.u == 16
    assert len(sceneobject.lines) == 16


def test_ellipse_object_uses_default_discretization(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    sceneobject = Viewer().scene.add(Ellipse(2.0, 1.0))

    assert sceneobject.u == 16
    assert len(sceneobject.lines) == 16
