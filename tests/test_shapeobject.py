from unittest.mock import Mock

import pytest

from compas.colors import Color
from compas.data import json_dumps
from compas.data import json_loads
from compas.geometry import Box
from compas.geometry import Capsule
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.geometry import PlanarSurface
from compas.geometry import Plane
from compas.geometry import Point
from compas.geometry import Sphere
from compas.geometry import Torus
from compas.geometry import Translation
from compas.geometry import Vector
from compas.scene import Scene
from compas_viewer import Viewer
from compas_viewer.scene import BufferObject
from compas_viewer.scene import GraphObject
from compas_viewer.scene import MeshObject
from compas_viewer.scene import ShapeObject
from compas_viewer.scene.scene import instance_colors_generator


@pytest.fixture
def viewer(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    viewer = Viewer()
    viewer.running = False
    viewer.scene.clear(clear_context=False)
    yield viewer
    viewer.running = False
    viewer.scene.clear(clear_context=False)


def test_shape_object_owns_default_resolution(viewer):
    shape = Sphere(1.0)

    sceneobject = viewer.scene.add(shape)

    assert sceneobject.u == 16
    assert sceneobject.v == 16
    assert not hasattr(shape, "resolution_u")
    assert not hasattr(shape, "resolution_v")


def test_shape_object_resolution_override_does_not_mutate_geometry(viewer):
    shape = Sphere(1.0)
    data = shape.__data__

    sceneobject = viewer.scene.add(shape, u=6, v=4)
    tessellation = sceneobject.tessellation

    assert sceneobject.u == 6
    assert sceneobject.v == 4
    assert tessellation.number_of_vertices == 20
    assert tessellation.number_of_triangles == 36
    assert shape.__data__ == data


def test_shape_object_scene_roundtrip_preserves_durable_state(viewer):
    shape = Sphere(1.0)
    transformation = Translation.from_vector([2, 0, 0])
    facecolor = Color.red()
    original = viewer.scene.add(
        shape,
        is_selected=True,
        show_faces=False,
        u=7,
        use_rgba=True,
        v=9,
        facecolor=facecolor,
        transformation=transformation,
    )
    original.background = True
    assert not hasattr(original, "settings")

    payload = json_dumps(viewer.scene)
    restored_scene = json_loads(payload)

    assert isinstance(restored_scene, Scene)
    assert "is_selected" not in payload
    restored_scene.bind(shape)
    restored_scene.bind_context("Viewer")
    restored = restored_scene.objects[0]
    assert restored.transformation == transformation
    assert restored.u == 7
    assert restored.v == 9
    assert restored.facecolor == facecolor
    assert restored.show_faces is False
    assert restored.use_rgba is True
    assert restored.background is True
    assert restored.is_selected is False


def test_geometry_adapter_scene_roundtrip_preserves_declared_state(viewer):
    frame = Frame.worldXY()
    plane = Plane.worldXY()
    vector = Vector(1, 2, 3)
    viewer.scene.add(frame, size=2.5)
    viewer.scene.add(plane, planesize=4.5)
    viewer.scene.add(vector, anchor=Point(5, 6, 7))

    restored_scene = json_loads(json_dumps(viewer.scene))
    restored_scene.bind_many([frame, plane, vector])
    restored_scene.bind_context("Viewer")
    restored_frame, restored_plane, restored_vector = restored_scene.objects

    assert restored_frame.size == 2.5
    assert restored_plane.planesize == 4.5
    assert restored_vector.anchor == Point(5, 6, 7)


@pytest.mark.parametrize("object_type", [ShapeObject, MeshObject, GraphObject, BufferObject])
def test_viewer_scene_state_mro_has_one_owner_per_adapter_attribute(object_type):
    declarations = object_type.scene_state_fields()
    attributes = [field.attribute for fields in declarations.values() for field in fields]

    assert len(attributes) == len(set(attributes))


def test_shape_object_uses_core_ownership_for_shared_geometry_state():
    declarations = ShapeObject.scene_state_fields()
    core_fields = {field.attribute for field in declarations["compas.scene.GeometryObject"]}
    viewer_fields = {field.attribute for field in declarations["compas_viewer.scene.ViewerSceneObject"]}

    assert {"show_points", "show_lines", "linewidth", "pointsize"} <= core_fields
    assert not {"show_points", "show_lines", "linewidth", "pointsize"} & viewer_fields


def test_instance_color_cache_resets_when_adapters_are_rebound(viewer):
    original = viewer.scene.add(Sphere(1.0))
    viewer.scene.instance_colors[(10, 20, 30)] = original

    viewer.scene.bind_context("Viewer")

    assert viewer.scene.objects[0] is not original
    assert viewer.scene.instance_colors == {}
    assert next(viewer.scene._instance_colors_generator) == next(instance_colors_generator())


def test_instance_color_cache_resets_when_scene_changes(viewer):
    sceneobject = viewer.scene.add(Sphere(1.0))
    viewer.scene.instance_colors[(10, 20, 30)] = sceneobject

    viewer.scene.remove(sceneobject, rebuild_buffers=False)

    assert viewer.scene.instance_colors == {}
    assert next(viewer.scene._instance_colors_generator) == next(instance_colors_generator())

    viewer.scene.instance_colors[(40, 50, 60)] = sceneobject
    viewer.scene.clear(clear_scene=False, clear_context=False)

    assert viewer.scene.instance_colors == {}
    assert next(viewer.scene._instance_colors_generator) == next(instance_colors_generator())


@pytest.mark.parametrize(
    ("shape", "u", "v", "vertices", "triangles"),
    [
        (Box(1.0), 6, 4, 8, 12),
        (Cone(1.0, 2.0), 6, 4, 8, 12),
        (Cylinder(1.0, 2.0), 6, 4, 14, 24),
        (Capsule(1.0, 2.0), 6, 4, 26, 48),
        (Sphere(1.0), 6, 4, 20, 36),
        (Torus(2.0, 0.5), 6, 4, 24, 48),
    ],
)
def test_shape_object_dispatches_producer_specific_resolution(viewer, shape, u, v, vertices, triangles):
    sceneobject = viewer.scene.add(shape, u=u, v=v)

    tessellation = sceneobject.tessellation

    assert tessellation.number_of_vertices == vertices
    assert tessellation.number_of_triangles == triangles


def test_shape_object_requests_fresh_representations(viewer):
    shape = Sphere(1.0)
    sceneobject = viewer.scene.add(shape, u=6, v=4)

    first = sceneobject.tessellation
    second = sceneobject.tessellation

    assert first is not second
    assert first.vertices is not second.vertices


def test_changing_shape_object_resolution_changes_tessellation(viewer):
    sceneobject = viewer.scene.add(Sphere(1.0), u=6, v=4)
    initial = sceneobject.tessellation

    sceneobject.u = 8
    sceneobject.v = 6
    updated = sceneobject.tessellation

    assert updated.number_of_vertices != initial.number_of_vertices
    assert updated.number_of_triangles != initial.number_of_triangles


def test_changing_active_shape_object_resolution_refreshes_and_rebuilds(viewer, monkeypatch):
    sceneobject = viewer.scene.add(Sphere(1.0), u=6, v=4)
    refresh_data = Mock()
    rebuild_buffers = Mock()
    update = Mock()
    monkeypatch.setattr(sceneobject, "refresh_data", refresh_data)
    monkeypatch.setattr(viewer.renderer, "rebuild_buffers", rebuild_buffers)
    monkeypatch.setattr(viewer.renderer, "update", update)
    viewer.running = True

    sceneobject.u = 8

    refresh_data.assert_called_once_with()
    rebuild_buffers.assert_called_once_with()
    update.assert_called_once_with()


def test_surface_object_uses_scene_owned_resolution_without_mutation(viewer):
    surface = PlanarSurface()
    data = surface.__data__

    sceneobject = viewer.scene.add(surface, u=2, v=3)
    tessellation = sceneobject.tessellation

    assert tessellation.number_of_vertices == 12
    assert tessellation.number_of_triangles == 12
    assert surface.__data__ == data
