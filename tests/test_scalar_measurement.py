from math import inf
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest

from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Polygon
from compas.geometry import Polyhedron
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Transformation
from compas.geometry import Translation
from compas.scene import Group
from compas.scene import Scene
from compas.scene import SceneObject
from compas_viewer import Viewer
from compas_viewer._scalar_measurement import ScalarMeasurementError
from compas_viewer._scalar_measurement import UnsupportedScalarMeasurementError
from compas_viewer._scalar_measurement import measure_sceneobject_scalar
from compas_viewer.measurement import DistanceInspection
from compas_viewer.measurement import MeasurementState
from compas_viewer.scene import BufferGeometry


def sceneobject(item, transformation=None):
    return SceneObject(item=item, transformation=transformation)


def cube_mesh():
    vertices = [
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 1, 1],
    ]
    faces = [
        [0, 3, 2, 1],
        [4, 5, 6, 7],
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7],
    ]
    return Mesh.from_vertices_and_faces(vertices, faces)


def bare_viewer(selected):
    viewer = object.__new__(Viewer)
    viewer.state = SimpleNamespace(
        selection=SimpleNamespace(objects=tuple(selected)),
        annotation_selection=SimpleNamespace(objects=(object(),)),
        measurement=MeasurementState(),
    )
    viewer._undo_transforms = [object()]
    viewer._redo_transforms = [object()]
    return viewer


def test_public_area_and_volume_use_item_contracts_and_exact_uniform_scale():
    box = sceneobject(Box(1), Scale.from_factors([2, 2, 2]))
    area_viewer = bare_viewer([box])
    volume_viewer = bare_viewer([box])

    assert area_viewer.inspect_selected_area() == pytest.approx(24.0)
    assert volume_viewer.inspect_selected_volume() == pytest.approx(8.0)


def test_mesh_area_closed_volume_and_open_volume_rejection():
    mesh = cube_mesh()
    mesh_object = sceneobject(mesh)

    assert measure_sceneobject_scalar(mesh_object, "area") == pytest.approx(6.0)
    assert measure_sceneobject_scalar(mesh_object, "volume") == pytest.approx(1.0)

    mesh.delete_face(5)
    with pytest.raises(UnsupportedScalarMeasurementError, match="does not enclose"):
        measure_sceneobject_scalar(mesh_object, "volume")


def test_method_and_property_measurement_members_are_supported():
    method_item = SimpleNamespace(area=lambda: 3.5)
    property_item = SimpleNamespace(volume=2.25)
    method_object = cast(SceneObject, SimpleNamespace(item=method_item, worldtransformation=Transformation()))
    property_object = cast(SceneObject, SimpleNamespace(item=property_item, worldtransformation=Transformation()))

    assert measure_sceneobject_scalar(method_object, "area") == pytest.approx(3.5)
    assert measure_sceneobject_scalar(property_object, "volume") == pytest.approx(2.25)


def test_not_implemented_is_unsupported_but_other_item_errors_propagate():
    def not_implemented():
        raise NotImplementedError

    def failed():
        raise RuntimeError("backend failed")

    unsupported = cast(SceneObject, SimpleNamespace(item=SimpleNamespace(area=not_implemented), worldtransformation=Transformation()))
    broken = cast(SceneObject, SimpleNamespace(item=SimpleNamespace(area=failed), worldtransformation=Transformation()))

    with pytest.raises(UnsupportedScalarMeasurementError, match="does not implement"):
        measure_sceneobject_scalar(unsupported, "area")
    with pytest.raises(RuntimeError, match="backend failed"):
        measure_sceneobject_scalar(broken, "area")


def test_property_implementation_attribute_errors_are_not_reclassified_as_missing():
    class BrokenProperty:
        @property
        def area(self):
            raise AttributeError("implementation failed")

    broken = cast(SceneObject, SimpleNamespace(item=BrokenProperty(), worldtransformation=Transformation()))

    with pytest.raises(AttributeError, match="implementation failed"):
        measure_sceneobject_scalar(broken, "area")


def test_polygon_area_and_optional_backend_brep_properties():
    polygon = Polygon([[0, 0, 0], [2, 0, 0], [2, 1, 0], [0, 1, 0]])
    assert measure_sceneobject_scalar(sceneobject(polygon), "area") == pytest.approx(2.0)

    polyhedron = Polyhedron.from_platonicsolid(6)
    assert measure_sceneobject_scalar(sceneobject(polyhedron), "area") == pytest.approx(polyhedron.area())
    assert measure_sceneobject_scalar(sceneobject(polyhedron), "volume") == pytest.approx(polyhedron.volume())

    pytest.importorskip("compas_occ")
    from compas_occ.brep import OCCBrep

    brep = sceneobject(OCCBrep.from_box(Box(1)))
    assert measure_sceneobject_scalar(brep, "area") == pytest.approx(6.0)
    assert measure_sceneobject_scalar(brep, "volume") == pytest.approx(1.0)


def test_unsupported_items_and_unresolved_references_fail_explicitly():
    unsupported = [sceneobject(Graph()), sceneobject(BufferGeometry.from_points([[0, 0, 0]])), Group()]
    for obj in unsupported:
        with pytest.raises(UnsupportedScalarMeasurementError, match="does not provide"):
            measure_sceneobject_scalar(obj, "area")

    unresolved = SceneObject(item_guid=uuid4())
    with pytest.raises(UnsupportedScalarMeasurementError, match="no resolved data item"):
        measure_sceneobject_scalar(unresolved, "volume")


@pytest.mark.parametrize("value", [True, "1", object(), -1, inf, float("nan")])
def test_invalid_scalar_results_are_rejected(value):
    item = SimpleNamespace(area=value)
    obj = cast(SceneObject, SimpleNamespace(item=item, worldtransformation=Transformation()))

    with pytest.raises(ScalarMeasurementError, match="nonnegative finite number"):
        measure_sceneobject_scalar(obj, "area")


def test_area_accepts_reflection_and_inherited_uniform_world_scale():
    reflected = Scale.from_factors([-2, 2, 2])
    combined = Translation.from_vector([5, 6, 7]) * reflected
    obj = sceneobject(Box(1), combined)

    assert measure_sceneobject_scalar(obj, "area") == pytest.approx(24.0)


@pytest.mark.parametrize("scale", [1e-12, 1e120])
def test_area_accepts_rotated_uniform_scale_independently_of_magnitude(scale):
    rotation = Rotation.from_axis_and_angle([1, 2, 3], 0.713)
    transformation = rotation * Scale.from_factors([scale, scale, scale])
    area = measure_sceneobject_scalar(sceneobject(Box(1), transformation), "area")

    assert area > 0
    assert area == pytest.approx(6.0 * scale * scale, rel=1e-12, abs=0)


def test_area_uses_composed_parent_and_local_world_transformations():
    scene = Scene()
    parent = scene.add_group(
        "Parent",
        transformation=Translation.from_vector([4, 5, 6]) * Rotation.from_axis_and_angle([0, 0, 1], 0.4) * Scale.from_factors([3, 3, 3]),
    )
    child = scene.add(
        Box(1),
        parent=parent,
        transformation=Rotation.from_axis_and_angle([1, 0, 0], 0.8) * Scale.from_factors([2, 2, 2]),
    )

    assert measure_sceneobject_scalar(child, "area") == pytest.approx(216.0)


@pytest.mark.parametrize(
    "transformation",
    [
        Scale.from_factors([2, 3, 4]),
        Scale.from_factors([1e-12, 2e-12, 1e-12]),
        Transformation.from_matrix([[1, 0.5, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]),
    ],
)
def test_area_rejects_nonuniform_scale_and_shear(transformation):
    with pytest.raises(UnsupportedScalarMeasurementError, match="rigid, reflected, or uniformly scaled"):
        measure_sceneobject_scalar(sceneobject(Box(1), transformation), "area")


def test_area_rejects_degenerate_uniform_scale():
    degenerate = Transformation.from_matrix([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1]])

    with pytest.raises(UnsupportedScalarMeasurementError, match="finite nonzero uniform"):
        measure_sceneobject_scalar(sceneobject(Box(1), degenerate), "area")


def test_volume_uses_absolute_affine_determinant():
    transformation = Transformation.from_matrix([[-2, 0.5, 0, 4], [0, 3, 0, 5], [0, 0, 4, 6], [0, 0, 0, 1]])

    assert measure_sceneobject_scalar(sceneobject(Box(1), transformation), "volume") == pytest.approx(24.0)


@pytest.mark.parametrize("kind", ["area", "volume"])
def test_projective_transformations_are_rejected(kind):
    projective = Transformation.from_matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0.1, 0, 0, 1]])

    with pytest.raises(UnsupportedScalarMeasurementError, match="projective"):
        measure_sceneobject_scalar(sceneobject(Box(1), projective), kind)


@pytest.mark.parametrize("selected", [(), (sceneobject(Box(1)), sceneobject(Box(1)))])
def test_public_inspection_requires_exactly_one_selection_and_cancels_distance(selected):
    viewer = bare_viewer(selected)
    viewer.state.measurement.start("inspection")

    with pytest.raises(ValueError, match="exactly one"):
        viewer.inspect_selected_area()

    assert not viewer.state.measurement.has_transient_state


def test_public_inspection_clears_retained_distance_without_other_mutation():
    selected = sceneobject(Box(1))
    viewer = bare_viewer([selected])
    viewer.state.measurement.completed_inspection = DistanceInspection([0, 0, 0], [1, 0, 0])
    spatial_selection = viewer.state.selection.objects
    annotation_selection = viewer.state.annotation_selection.objects
    undo = list(viewer._undo_transforms)
    redo = list(viewer._redo_transforms)

    assert viewer.inspect_selected_volume() == pytest.approx(1.0)
    assert not viewer.state.measurement.has_transient_state
    assert viewer.state.selection.objects == spatial_selection
    assert viewer.state.annotation_selection.objects == annotation_selection
    assert viewer._undo_transforms == undo
    assert viewer._redo_transforms == redo
