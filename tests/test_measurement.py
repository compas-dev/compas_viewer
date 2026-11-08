from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from compas.geometry import Point
from compas.geometry import Sphere
from compas.scene import ComponentAnchor
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas_viewer import Viewer
from compas_viewer._history import TransformTransaction
from compas_viewer.config import Config
from compas_viewer.measurement import DistanceInspection
from compas_viewer.measurement import MeasurementState
from compas_viewer.plugins import ensure_scene_objects_registered
from compas_viewer.scene import ViewerScene
from compas_viewer.snapping import SnapKind
from compas_viewer.snapping import SnapResult
from compas_viewer.state import ViewerState


def snap(
    xyz,
    *,
    kind=SnapKind.POINT,
    object_guid=None,
    component=None,
    parameter=None,
    association_error=None,
):
    return SnapResult(
        Point(*xyz),
        object_guid or uuid4(),
        kind,
        0.0,
        component=component,
        parameter=parameter,
        association_error=association_error,
    )


def connected_viewer(*, results=()):
    ensure_scene_objects_registered()
    scene = ViewerScene()
    renderer = Mock()
    renderer.query_snap_at.side_effect = results
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
    state.accept(snap([0, 0, 0]), unit=None, precision=3)
    completed = state.accept(snap([3, 4, 0]), unit=None, precision=3)

    assert isinstance(completed, DistanceInspection)
    assert completed.distance == 5.0
    assert not state.active
    assert state.completed_inspection is completed

    state.start("fixed")

    assert state.active
    assert state.mode == "fixed"
    assert state.completed_inspection is None
    assert state.first_snap is None


def test_background_clears_hover_without_clearing_first_anchor():
    state = MeasurementState()
    first = snap([0, 0, 0])
    state.start("fixed")
    state.accept(first, unit=None, precision=3)
    state.update_hover(snap([1, 0, 0]))

    state.accept(None, unit=None, precision=3)

    assert state.first_snap is first
    assert state.hover_snap is None
    assert state.active


def test_fixed_dimensions_accept_fixed_only_surface_snaps_and_copy_points():
    state = MeasurementState()
    first = snap([0, 0, 0], kind=SnapKind.FACE, association_error="Fixed only")
    second = snap([2, 0, 0], kind=SnapKind.SURFACE, association_error="Fixed only")
    state.start("fixed")
    state.accept(first, unit="mm", precision=4)

    result = state.accept(second, unit="mm", precision=4)
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
    first = snap([0, 0, 0], kind=SnapKind.FACE, association_error="Face snaps are fixed only")
    state.start("associative")

    result = state.accept(first, unit=None, precision=3)

    assert result is None
    assert state.first_snap is None
    assert state.hover_snap is first
    assert state.rejection == "Face snaps are fixed only"
    assert state.active


def test_associative_dimensions_keep_component_anchors():
    state = MeasurementState()
    first_guid = uuid4()
    second_guid = uuid4()
    first = snap([0, 0, 0], object_guid=first_guid, kind=SnapKind.VERTEX, component=1)
    second = snap([2, 0, 0], object_guid=second_guid, kind=SnapKind.EDGE, component=(2, 3), parameter=0.25)
    state.start("associative")
    state.accept(first, unit=None, precision=3)

    result = state.accept(second, unit=None, precision=3)

    assert isinstance(result, DistanceDimension)
    assert result.start == ComponentAnchor(first_guid, "vertex", component=1)
    assert result.end == ComponentAnchor(second_guid, "edge", component=(2, 3), parameter=0.25)


@pytest.mark.parametrize(
    ("kind", "component", "parameter"),
    [
        (SnapKind.POINT, None, None),
        (SnapKind.VERTEX, 1, None),
        (SnapKind.NODE, "a", None),
        (SnapKind.LINE, None, 0.25),
        (SnapKind.EDGE, (1, 2), 0.25),
    ],
)
def test_associative_measurement_accepts_every_supported_snap_kind(kind, component, parameter):
    state = MeasurementState()
    state.start("associative")
    state.accept(snap([0, 0, 0], kind=kind, component=component, parameter=parameter), unit=None, precision=3)

    result = state.accept(snap([1, 0, 0], kind=kind, component=component, parameter=parameter), unit=None, precision=3)

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
    assert renderer.query_snap_at.call_count == 2


def test_new_measurement_scene_replacement_and_scene_clear_cancel_transient_state():
    viewer, scene, _ = connected_viewer()
    viewer.start_distance_inspection()
    viewer.state.measurement.accept(snap([0, 0, 0]), unit=None, precision=3)

    viewer.scene = ViewerScene()

    assert not viewer.state.measurement.has_transient_state

    viewer.start_distance_dimension("fixed")
    viewer.state.measurement.accept(snap([0, 0, 0]), unit=None, precision=3)
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
