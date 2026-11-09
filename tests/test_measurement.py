from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from compas.datastructures import Mesh
from compas.geometry import Point
from compas.geometry import Sphere
from compas.geometry import distance_point_point
from compas.scene import ComponentAnchor
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import SceneObject
from compas_viewer import Viewer
from compas_viewer._history import TransformTransaction
from compas_viewer.config import Config
from compas_viewer.measurement import DistanceInspection
from compas_viewer.measurement import MeasurementState
from compas_viewer.plugins import ensure_scene_objects_registered
from compas_viewer.scene import ViewerScene
from compas_viewer.snapping import ProjectedPoint
from compas_viewer.snapping import SnapKind
from compas_viewer.snapping import SnapQuery
from compas_viewer.snapping import SnapResult
from compas_viewer.snapping import query_snaps
from compas_viewer.state import ViewerState


def snap(
    xyz,
    *,
    kind=SnapKind.POINT,
    object_guid=None,
    component=None,
    association_error=None,
):
    return SnapResult(
        Point(*xyz),
        object_guid or uuid4(),
        kind,
        0.0,
        component=component,
        association_error=association_error,
    )


def query(result=None, points=()):
    return SnapQuery(result, points)


def connected_viewer(*, results=()):
    ensure_scene_objects_registered()
    scene = ViewerScene()
    renderer = Mock()
    if results:
        renderer.query_snap_context_at.side_effect = [query(result) for result in results]
    viewer = object.__new__(Viewer)
    viewer._config = Config()
    viewer._scene = scene
    viewer._undo_transforms = []
    viewer._redo_transforms = []
    viewer.running = False
    viewer.ui = SimpleNamespace(viewport=SimpleNamespace(renderer=renderer), sidebar=Mock())  # type: ignore[assignment]
    viewer.state = ViewerState(viewer.config, scene.object)
    viewer.state.changed.connect(viewer._on_state_changed)
    scene.attach(viewer)
    return viewer, scene, renderer


def test_measurement_state_activation_clears_previous_mode_and_result():
    state = MeasurementState()
    state.start("inspection")
    state.accept(query(snap([0, 0, 0])), unit=None, precision=3)
    completed = state.accept(query(snap([3, 4, 0])), unit=None, precision=3)

    assert isinstance(completed, DistanceInspection)
    assert completed.distance == 5.0
    assert not state.active
    assert state.completed_inspection is completed

    state.start("fixed")

    assert state.active
    assert state.mode == "fixed"
    assert state.completed_inspection is None
    assert state.first_snap is None


def test_four_by_three_mesh_acquisition_creates_exact_five_unit_dimension():
    mesh = Mesh.from_vertices_and_faces(
        [[0, 0, 0], [4, 0, 0], [4, 3, 0], [0, 3, 0]],
        [[0, 1, 2, 3]],
    )
    sceneobject = SceneObject(mesh)

    def project(point):
        return ProjectedPoint(point.x, point.y, point.z)

    first = query_snaps([sceneobject], (0, 0), radius=0, project=project)
    second = query_snaps([sceneobject], (4, 3), radius=0, project=project)
    state = MeasurementState()
    state.start("fixed")

    assert first.winner is not None
    assert first.winner.kind is SnapKind.VERTEX
    assert first.winner.component == 0
    assert second.winner is not None
    assert second.winner.kind is SnapKind.VERTEX
    assert second.winner.component == 2
    assert state.accept(first, unit="m", precision=2) is None
    dimension = state.accept(second, unit="m", precision=2)

    assert isinstance(dimension, DistanceDimension)
    resolved = dimension.resolve()
    assert resolved is not None
    assert resolved == (Point(0, 0, 0), Point(4, 3, 0))
    assert distance_point_point(*resolved) == 5.0


def test_background_clears_hover_without_clearing_first_anchor():
    state = MeasurementState()
    first = snap([0, 0, 0])
    state.start("fixed")
    state.accept(query(first), unit=None, precision=3)
    state.update_hover(SnapQuery(snap([1, 0, 0]), (snap([2, 0, 0]),)))

    state.accept(query(), unit=None, precision=3)

    assert state.first_snap is first
    assert state.hover_snap is None
    assert state.available_points == ()
    assert state.active


def test_hover_point_palette_follows_context_and_clears_on_cancel_and_completion():
    state = MeasurementState()
    first = snap([0, 0, 0])
    first_palette = (first, snap([1, 0, 0]))
    second = snap([2, 0, 0])
    second_palette = (second, snap([3, 0, 0]))
    state.start("fixed")

    state.update_hover(SnapQuery(first, first_palette))
    state.accept(query(first, first_palette), unit=None, precision=3)

    assert state.available_points == first_palette
    assert state.first_snap is first

    state.update_hover(SnapQuery(second, second_palette))

    assert state.available_points == second_palette
    assert state.first_snap is first

    result = state.accept(query(second, second_palette), unit=None, precision=3)

    assert isinstance(result, DistanceDimension)
    assert state.available_points == ()

    state.start("inspection")
    state.update_hover(SnapQuery(first, first_palette))
    assert state.cancel()
    assert state.available_points == ()


def test_viewer_hover_stores_renderer_snap_context():
    winner = snap([0, 0, 0])
    query = SnapQuery(winner, (winner, snap([1, 0, 0])))
    viewer, _, renderer = connected_viewer()
    renderer.query_snap_context_at.return_value = query
    viewer.start_distance_dimension("fixed")

    viewer._update_measurement_hover((10, 20))

    assert viewer.state.measurement.hover_snap is winner
    assert viewer.state.measurement.available_points == query.points
    renderer.query_snap_context_at.assert_called_once_with((10, 20), 18.0)


def test_click_before_hover_keeps_associative_rejection_and_point_palette():
    unstable = snap([1, 1, 0], kind=SnapKind.NODE, association_error="The node key is not serializable")
    palette = (
        snap([0, 0, 0], kind=SnapKind.VERTEX, component=0),
        snap([2, 0, 0], kind=SnapKind.VERTEX, component=1),
    )
    viewer, _, renderer = connected_viewer()
    renderer.query_snap_context_at.return_value = SnapQuery(unstable, palette)
    viewer.start_distance_dimension("associative")

    viewer._accept_measurement_at((10, 20))

    measurement = viewer.state.measurement
    assert measurement.first_snap is None
    assert measurement.hover_snap is unstable
    assert measurement.available_points == palette
    assert measurement.rejection == "The node key is not serializable"


def test_click_replaces_stale_hover_palette_atomically():
    stale = snap([0, 0, 0])
    stale_query = SnapQuery(stale, (stale, snap([1, 0, 0])))
    winner = snap([10, 0, 0])
    current_query = SnapQuery(winner, (winner, snap([11, 0, 0])))
    viewer, _, renderer = connected_viewer()
    renderer.query_snap_context_at.return_value = stale_query
    viewer.start_distance_dimension("fixed")
    viewer._update_measurement_hover((1, 1))
    renderer.query_snap_context_at.return_value = current_query

    viewer._accept_measurement_at((10, 20))

    measurement = viewer.state.measurement
    assert measurement.first_snap is winner
    assert measurement.hover_snap is winner
    assert measurement.available_points == current_query.points


def test_fixed_dimensions_accept_nonassociative_discrete_snaps_and_copy_points():
    state = MeasurementState()
    first = snap([0, 0, 0], kind=SnapKind.NODE, association_error="Unstable key")
    second = snap([2, 0, 0], kind=SnapKind.NODE, association_error="Unstable key")
    state.start("fixed")
    state.accept(query(first), unit="mm", precision=4)

    result = state.accept(query(second), unit="mm", precision=4)
    first.point.x = 100
    second.point.x = 200

    assert isinstance(result, DistanceDimension)
    assert isinstance(result.start, PointAnchor)
    assert isinstance(result.end, PointAnchor)
    assert result.start.point == Point(0, 0, 0)
    assert result.end.point == Point(2, 0, 0)
    assert result.unit == "mm"
    assert result.precision == 4


def test_associative_dimensions_reject_unsupported_snaps_without_fallback():
    state = MeasurementState()
    first = snap([0, 0, 0], kind=SnapKind.NODE, association_error="Unstable key")
    state.start("associative")

    result = state.accept(query(first), unit=None, precision=3)

    assert result is None
    assert state.first_snap is None
    assert state.hover_snap is first
    assert state.rejection == "Unstable key"
    assert state.active


def test_associative_dimensions_keep_component_anchors():
    state = MeasurementState()
    first_guid = uuid4()
    second_guid = uuid4()
    first = snap([0, 0, 0], object_guid=first_guid, kind=SnapKind.VERTEX, component=1)
    second = snap([2, 0, 0], object_guid=second_guid, kind=SnapKind.NODE, component="end")
    state.start("associative")
    state.accept(query(first), unit=None, precision=3)

    result = state.accept(query(second), unit=None, precision=3)

    assert isinstance(result, DistanceDimension)
    assert result.start == ComponentAnchor(first_guid, "vertex", component=1)
    assert result.end == ComponentAnchor(second_guid, "node", component="end")


@pytest.mark.parametrize(
    ("kind", "component"),
    [
        (SnapKind.POINT, None),
        (SnapKind.VERTEX, 1),
        (SnapKind.NODE, "a"),
    ],
)
def test_associative_measurement_accepts_every_supported_snap_kind(kind, component):
    state = MeasurementState()
    state.start("associative")
    state.accept(query(snap([0, 0, 0], kind=kind, component=component)), unit=None, precision=3)

    result = state.accept(query(snap([1, 0, 0], kind=kind, component=component)), unit=None, precision=3)

    assert isinstance(result, DistanceDimension)
    assert isinstance(result.start, ComponentAnchor)
    assert isinstance(result.end, ComponentAnchor)


def test_transient_inspection_does_not_mutate_scene_selection_or_history():
    viewer, scene, _ = connected_viewer(results=(snap([0, 0, 0]), snap([3, 4, 0])))
    selected = scene.add(Sphere(1))
    viewer.state.selection.add(selected)
    history = TransformTransaction(before=(), after=())
    viewer._undo_transforms.append(history)
    before_objects = tuple(scene.objects)

    viewer.start_distance_inspection()
    viewer._accept_measurement_at((10, 20))
    viewer._accept_measurement_at((30, 40))

    assert tuple(scene.objects) == before_objects
    assert viewer.state.selection.objects == (selected,)
    assert viewer._undo_transforms == [history]
    inspection = viewer.state.measurement.completed_inspection
    assert inspection is not None
    assert inspection.distance == 5.0


@pytest.mark.parametrize("mode", ["fixed", "associative"])
def test_persistent_completion_adds_one_root_dimension_and_selects_it(mode):
    first_guid = uuid4()
    second_guid = uuid4()
    if mode == "fixed":
        results = (snap([0, 0, 0]), snap([2, 0, 0]))
    else:
        results = (
            snap([0, 0, 0], object_guid=first_guid),
            snap([2, 0, 0], object_guid=second_guid),
        )
    viewer, scene, renderer = connected_viewer(results=results)
    viewer.state.set_measurement_unit("cm")
    viewer.state.set_measurement_precision(1)
    viewer.start_distance_dimension(mode)

    viewer._accept_measurement_at((10, 20))
    viewer._accept_measurement_at((30, 40))

    assert len(scene.objects) == 1
    created = scene.objects[0]
    assert created.parent is not None and created.parent.is_root
    assert isinstance(created.item, DistanceDimension)
    assert created.item.unit == "cm"
    assert created.item.precision == 1
    assert viewer.state.selection.objects == (created,)
    assert not viewer.state.measurement.active
    assert renderer.query_snap_context_at.call_count == 2


def test_new_measurement_scene_replacement_and_scene_clear_cancel_transient_state():
    viewer, scene, _ = connected_viewer()
    viewer.start_distance_inspection()
    viewer.state.measurement.accept(query(snap([0, 0, 0])), unit=None, precision=3)

    viewer.scene = ViewerScene()

    assert not viewer.state.measurement.has_transient_state

    viewer.start_distance_dimension("fixed")
    viewer.state.measurement.accept(query(snap([0, 0, 0])), unit=None, precision=3)
    viewer.scene.clear()

    assert not viewer.state.measurement.has_transient_state


def test_cancel_measurement_reports_active_and_retained_state():
    viewer, _, _ = connected_viewer()

    assert not viewer.cancel_measurement()
    viewer.start_distance_inspection()
    assert viewer.cancel_measurement()
    assert not viewer.cancel_measurement()


def test_distance_dimension_mode_is_explicit():
    viewer, _, _ = connected_viewer()

    with pytest.raises(ValueError, match="Unsupported distance measurement mode"):
        viewer.start_distance_dimension("mixed")  # type: ignore[arg-type]
