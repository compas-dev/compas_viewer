from unittest.mock import Mock

import pytest

from compas.colors import Color
from compas.data import json_dumps
from compas.data import json_loads
from compas.geometry import Frame
from compas.geometry import Box
from compas.geometry import Capsule
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Plane
from compas.geometry import Sphere
from compas.geometry import Torus
from compas.geometry import Translation
from compas.geometry import Vector
from compas.scene import FrameObject
from compas.scene import PlaneObject
from compas.scene import Scene
from compas.scene import ShapeObject
from compas.scene import VectorObject
from compas_viewer import Viewer
from compas_viewer.commands import zoom_extents
from compas_viewer.scene.shapeobject import ShapeObject as ViewerShapeObject
from compas_viewer.scene.vectorobject import VectorObject as ViewerVectorObject


@pytest.fixture
def viewer(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    viewer = Viewer()
    viewer.running = False
    viewer.scene.clear(clear_context=False)
    yield viewer
    viewer.running = False
    viewer.scene.clear(clear_context=False)


def test_viewer_scene_keeps_stable_core_type_and_runtime_state_separate(viewer):
    sceneobject = viewer.scene.add(Sphere(1.0), u=6, v=4)
    render_object = viewer.scene.render_object(sceneobject)

    assert type(sceneobject) is ShapeObject
    assert isinstance(render_object, ViewerShapeObject)
    assert render_object.sceneobject is sceneobject
    assert viewer.scene.objects[0] is sceneobject


def test_render_helper_construction_does_not_mutate_hidden_stable_object(viewer):
    sceneobject = viewer.scene.add(Sphere(1.0), show=False, u=6, v=4)
    durable_state = sceneobject.__data__

    render_object = viewer.scene.render_object(sceneobject)
    zoom_extents(viewer)

    assert render_object.sceneobject is sceneobject
    assert sceneobject.__data__ == durable_state
    assert sceneobject.show is False


def test_scene_draw_accepts_explicit_viewer_runtime(viewer):
    sceneobject = viewer.scene.add(Sphere(1.0))

    viewer.scene.draw(context="Viewer", runtime=viewer)
    render_object = viewer.scene.render_objects[sceneobject.guid]

    assert render_object.runtime is viewer
    assert render_object.runtime_scene is viewer.scene
    assert render_object.viewer is viewer


def test_shape_object_owns_default_resolution(viewer):
    sceneobject = viewer.scene.add(Sphere(1.0))

    assert sceneobject.u == 16
    assert sceneobject.v == 16


def test_shape_resolution_is_durable_without_serializing_runtime(viewer):
    shape = Sphere(1.0)
    sceneobject = viewer.scene.add(shape, u=7, v=9, transformation=Translation.from_vector([2, 0, 0]))
    viewer.state.selection.add(sceneobject)
    viewer.scene.render_object(sceneobject).init()

    payload = json_dumps(viewer.scene)
    restored = json_loads(payload)

    assert isinstance(restored, Scene)
    restored.bind(shape)
    assert type(restored.objects[0]) is ShapeObject
    assert restored.objects[0].u == 7
    assert restored.objects[0].v == 9
    assert "render_objects" not in payload
    assert "instance_color" not in payload
    assert "is_selected" not in payload
    assert '"selection"' not in payload


def test_stable_specialized_geometry_fields_use_core_names(viewer):
    frame = viewer.scene.add(Frame.worldXY(), size=2.5)
    plane = viewer.scene.add(Plane.worldXY(), size=4.5)
    vector = viewer.scene.add(Vector(1, 2, 3), anchor=[5, 6, 7])

    assert type(frame) is FrameObject and frame.size == 2.5
    assert type(plane) is PlaneObject and plane.size == 4.5
    assert type(vector) is VectorObject and list(vector.anchor) == [5, 6, 7]
    with pytest.raises(TypeError, match="planesize"):
        viewer.scene.add(Plane.worldXY(), planesize=2.0)


def test_vector_rendering_uses_stable_scene_object_color(viewer):
    sceneobject = viewer.scene.add(Vector(1, 0, 0), linecolor=Color.red())
    render_object = viewer.scene.render_object(sceneobject)

    assert isinstance(render_object, ViewerVectorObject)
    render_object._calculate_arrow_buffer_data()

    assert render_object._arrow_colors == [sceneobject.linecolor] * 7


def test_context_preparation_preserves_stable_identity(viewer):
    sceneobject = viewer.scene.add(Sphere(1.0))
    viewer.scene.prepare()
    first = viewer.scene.render_object(sceneobject)
    viewer.scene.prepare()
    second = viewer.scene.render_object(sceneobject)

    assert viewer.scene.objects[0] is sceneobject
    assert first is not second
    assert second.sceneobject is sceneobject


def test_viewer_scene_setter_preserves_bound_item_identity(viewer):
    shape = Sphere(1.0)
    source = Scene(context=None, _detect_context=False)
    source_object = source.add(shape)

    viewer.scene = source

    adopted = viewer.scene.objects[0]
    assert adopted.guid == source_object.guid
    assert adopted.item is shape


def test_viewer_adopts_existing_viewer_scene_without_rebuilding(viewer):
    source = viewer.scene.__class__()
    shape = Sphere(1.0)
    source_object = source.add(shape)

    viewer.scene = source

    assert viewer.scene is source
    assert viewer.scene.objects[0] is source_object
    assert viewer.scene.objects[0].item is shape


def test_shape_render_helper_uses_stable_resolution(viewer):
    sceneobject = viewer.scene.add(Sphere(1.0), u=6, v=4)
    render_object = viewer.scene.render_object(sceneobject)

    assert render_object.tessellation.number_of_vertices == 20
    assert render_object.tessellation.number_of_triangles == 36
    sceneobject.u = 8
    sceneobject.v = 6
    assert render_object.tessellation.number_of_vertices == 42


@pytest.mark.parametrize(
    ("shape", "vertices", "triangles"),
    [
        (Box(1.0), 8, 12),
        (Cone(1.0, 2.0), 8, 12),
        (Cylinder(1.0, 2.0), 14, 24),
        (Capsule(1.0, 2.0), 26, 48),
        (Sphere(1.0), 20, 36),
        (Torus(2.0, 0.5), 24, 48),
    ],
)
def test_shape_render_helper_dispatches_nonmutating_representations(viewer, shape, vertices, triangles):
    data = shape.__data__
    sceneobject = viewer.scene.add(shape, u=6, v=4)
    render_object = viewer.scene.render_object(sceneobject)

    first = render_object.tessellation
    second = render_object.tessellation

    assert first.number_of_vertices == vertices
    assert first.number_of_triangles == triangles
    assert first is not second
    assert first.vertices is not second.vertices
    assert shape.__data__ == data


def test_runtime_resolution_refresh_does_not_add_fields_to_stable_object(viewer, monkeypatch):
    sceneobject = viewer.scene.add(Sphere(1.0), u=6, v=4)
    render_object = viewer.scene.render_object(sceneobject)
    refresh_data = Mock()
    monkeypatch.setattr(render_object, "refresh_data", refresh_data)

    sceneobject.u = 8
    render_object._rebuild_resolution_buffers()

    assert sceneobject.u == 8
    assert not hasattr(sceneobject, "_points_data")


def test_active_resolution_refresh_rebuilds_runtime_buffers(viewer, monkeypatch):
    sceneobject = viewer.scene.add(Sphere(1.0), u=6, v=4)
    render_object = viewer.scene.render_object(sceneobject)
    refresh_data = Mock()
    rebuild_buffers = Mock()
    update = Mock()
    monkeypatch.setattr(render_object, "refresh_data", refresh_data)
    monkeypatch.setattr(viewer.renderer, "rebuild_buffers", rebuild_buffers)
    monkeypatch.setattr(viewer.renderer, "update", update)
    viewer.running = True

    sceneobject.u = 8
    render_object._rebuild_resolution_buffers()

    refresh_data.assert_called_once_with()
    rebuild_buffers.assert_called_once_with()
    update.assert_called_once_with()
