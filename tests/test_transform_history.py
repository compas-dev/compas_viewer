from types import SimpleNamespace
from unittest.mock import Mock
from math import pi

import pytest

from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import Sphere
from compas.geometry import Transformation
from compas.geometry import Translation
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import SceneObject
from compas_viewer import Viewer
from compas_viewer.config import Config
from compas_viewer.plugins import ensure_scene_objects_registered
from compas_viewer.scene import ViewerScene
from compas_viewer.scene.buffermanager import BufferManager
from compas_viewer.state import ViewerState


def connected_viewer(*, running: bool = False):
    scene = ViewerScene()
    manager = Mock()
    renderer = Mock()
    renderer.buffer_manager = manager
    sidebar = Mock()
    viewer = object.__new__(Viewer)
    viewer._config = Config()
    viewer._scene = scene
    viewer._undo_transforms = []
    viewer._redo_transforms = []
    viewer.running = running
    viewer.ui = SimpleNamespace(
        viewport=SimpleNamespace(renderer=renderer),
        sidebar=sidebar,
    )
    viewer.state = ViewerState(viewer.config, scene.object, scene.annotation)
    viewer.state.changed.connect(viewer._on_state_changed)
    scene.attach(viewer)
    return viewer, scene, renderer, sidebar


def test_world_transform_under_parent_is_atomic_and_reversible():
    viewer, scene, _, _ = connected_viewer()
    group = scene.add_group("Group", transformation=Translation.from_vector([10, 0, 0]))
    first = scene.add(Sphere(1), parent=group, transformation=Translation.from_vector([1, 0, 0]))
    second = scene.add(Sphere(1), parent=group)

    viewer.transform_objects((first, second, first), Translation.from_vector([0, 2, 0]))

    assert first.transformation == Translation.from_vector([1, 2, 0])
    assert second.transformation == Translation.from_vector([0, 2, 0])
    assert first.worldtransformation == Translation.from_vector([11, 2, 0])
    assert second.worldtransformation == Translation.from_vector([10, 2, 0])

    assert viewer.undo()
    assert first.transformation == Translation.from_vector([1, 0, 0])
    assert second.transformation is None
    assert not viewer.undo()

    assert viewer.redo()
    assert first.transformation == Translation.from_vector([1, 2, 0])
    assert second.transformation == Translation.from_vector([0, 2, 0])
    assert not viewer.redo()


def test_world_delta_is_left_multiplied_under_a_rotated_parent():
    viewer, scene, _, _ = connected_viewer()
    rotation = Rotation.from_axis_and_angle([0, 0, 1], pi / 2)
    group = scene.add_group("Rotated", transformation=rotation)
    child = scene.add(Sphere(1), parent=group, transformation=Translation.from_vector([1, 0, 0]))
    previous_local = child.transformation.copy()
    previous_world = child.worldtransformation.copy()
    delta = Translation.from_vector([2, 0, 0])

    viewer.transform_objects([child], delta)

    assert child.worldtransformation == delta * previous_world
    assert child.transformation == group.worldtransformation.inverse() * delta * previous_world
    assert child.transformation != delta * previous_local

    assert viewer.undo()
    assert child.transformation == previous_local
    assert child.worldtransformation == previous_world


def test_new_transform_invalidates_redo_without_affecting_previous_undo():
    viewer, scene, _, _ = connected_viewer()
    sceneobject = scene.add(Sphere(1))

    viewer.transform_objects([sceneobject], Translation.from_vector([1, 0, 0]))
    assert viewer.undo()
    viewer.transform_objects([sceneobject], Translation.from_vector([0, 2, 0]))

    assert not viewer.redo()
    assert viewer.undo()
    assert sceneobject.transformation is None


def test_transform_validation_leaves_objects_and_history_unchanged():
    viewer, scene, _, _ = connected_viewer()
    group = scene.add_group("Group", transformation=Translation.from_vector([1, 0, 0]))
    child = scene.add(Sphere(1), parent=group)
    foreign = SceneObject(name="Foreign")

    with pytest.raises(ValueError, match="ancestor and its descendant"):
        viewer.transform_objects([group, child], Translation.from_vector([0, 1, 0]))
    with pytest.raises(ValueError, match="current Viewer scene"):
        viewer.transform_objects([foreign], Translation.from_vector([0, 1, 0]))
    with pytest.raises(ValueError, match="Unsupported transformation space"):
        viewer.transform_objects([child], Translation.from_vector([0, 1, 0]), space="local")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="Transformation"):
        viewer.transform_objects([child], object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="SceneObject"):
        viewer.transform_objects([object()], Translation.from_vector([0, 1, 0]))  # type: ignore[list-item]

    assert group.transformation == Translation.from_vector([1, 0, 0])
    assert child.transformation is None
    assert not viewer.undo()


def test_singular_parent_failure_is_atomic():
    viewer, scene, _, _ = connected_viewer()
    group = scene.add_group("Group", transformation=Scale.from_factors([0, 1, 1]))
    child = scene.add(Sphere(1), parent=group)

    with pytest.raises(ValueError):
        viewer.transform_objects([child], Translation.from_vector([0, 1, 0]))

    assert child.transformation is None
    assert not viewer.undo()


def test_empty_and_identity_transform_are_history_noops():
    viewer, scene, _, _ = connected_viewer()
    sceneobject = scene.add(Sphere(1))

    viewer.transform_objects([], Translation.from_vector([1, 0, 0]))
    viewer.transform_objects([sceneobject], Transformation())

    assert sceneobject.transformation is None
    assert not viewer.undo()


def test_external_transform_refresh_and_hierarchy_mutation_clear_history():
    viewer, scene, _, _ = connected_viewer()
    first = scene.add(Sphere(1))
    second = scene.add(Sphere(1))
    viewer.transform_objects([first], Translation.from_vector([1, 0, 0]))

    viewer.refresh_transform([first])

    assert not viewer.undo()
    viewer.transform_objects([second], Translation.from_vector([0, 1, 0]))
    scene.remove(first, rebuild_buffers=False)
    assert not viewer.undo()


def test_failed_refresh_rolls_back_the_complete_transform_transaction():
    viewer, scene, renderer, _ = connected_viewer(running=True)
    first = scene.add(Sphere(1))
    second = scene.add(Sphere(1))
    scene.prepare()
    renderer.buffer_manager.update_object_transform.side_effect = RuntimeError("upload failed")

    with pytest.raises(RuntimeError, match="upload failed"):
        viewer.transform_objects((first, second), Translation.from_vector([1, 0, 0]))

    assert first.transformation is None
    assert second.transformation is None
    assert not viewer.undo()


def test_transform_refresh_updates_only_transform_buffers_and_syncs_once():
    viewer, scene, renderer, sidebar = connected_viewer(running=True)
    group = scene.add_group("Group")
    child = scene.add(Sphere(1), parent=group)
    scene.prepare()
    renderer.reset_mock()
    renderer.buffer_manager.reset_mock()
    sidebar.reset_mock()

    viewer.transform_objects([group], Translation.from_vector([1, 2, 3]))

    renderer.rebuild_buffers.assert_not_called()
    renderer.buffer_manager.update_object_transform.assert_called_once_with(scene.render_object(group))
    sidebar.update.assert_called_once_with()
    renderer.update.assert_called_once_with()
    assert child.worldtransformation == Translation.from_vector([1, 2, 3])


def test_transforming_parent_moves_cached_child_bounds_without_geometry_rebuild():
    viewer, scene, renderer, _ = connected_viewer(running=True)
    group = scene.add_group("Group")
    child = scene.add(Sphere(1), parent=group)
    scene.prepare()
    for render_object in scene.render_objects.values():
        render_object.init()
    child_render = scene.render_object(child)
    previous_center = child_render.bounding_box_center.copy()
    renderer.reset_mock()
    renderer.buffer_manager.reset_mock()

    viewer.transform_objects([group], Translation.from_vector([4, -2, 3]))

    assert child_render.bounding_box_center.x == pytest.approx(previous_center.x + 4)
    assert child_render.bounding_box_center.y == pytest.approx(previous_center.y - 2)
    assert child_render.bounding_box_center.z == pytest.approx(previous_center.z + 3)
    renderer.rebuild_buffers.assert_not_called()
    renderer.buffer_manager.update_object_data.assert_not_called()


def test_annotation_entries_are_not_spatial_transform_targets():
    viewer, scene, _, _ = connected_viewer()
    annotation = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])),
    )

    assert annotation not in scene.objects
    with pytest.raises(TypeError, match="SceneObject"):
        viewer.transform_objects([annotation], Translation.from_vector([10, 0, 0]))


def test_refresh_categories_have_distinct_buffer_scope():
    viewer, scene, renderer, sidebar = connected_viewer(running=True)
    sceneobject = scene.add(Sphere(1))
    scene.prepare()
    render_object = scene.render_object(sceneobject)
    renderer.reset_mock()
    renderer.buffer_manager.reset_mock()
    sidebar.reset_mock()

    viewer.refresh_appearance([sceneobject])

    renderer.buffer_manager.update_object_data.assert_called_once_with(render_object)
    renderer.buffer_manager.update_object_settings.assert_called_once_with(render_object)
    renderer.rebuild_buffers.assert_not_called()
    sidebar.update.assert_called_once_with()
    renderer.update.assert_called_once_with()

    renderer.reset_mock()
    sidebar.update.reset_mock()
    viewer.refresh_geometry([sceneobject])

    renderer.rebuild_buffers.assert_called_once_with()
    sidebar.update.assert_called_once_with()
    renderer.update.assert_called_once_with()


def test_geometry_and_appearance_refresh_preserve_transform_history():
    viewer, scene, _, _ = connected_viewer()
    sceneobject = scene.add(Sphere(1))

    viewer.transform_objects([sceneobject], Translation.from_vector([1, 0, 0]))
    viewer.refresh_geometry([sceneobject])
    assert viewer.undo()
    assert sceneobject.transformation is None

    viewer.transform_objects([sceneobject], Translation.from_vector([0, 2, 0]))
    viewer.refresh_appearance([sceneobject])
    assert viewer.undo()
    assert sceneobject.transformation is None


def test_hierarchy_refresh_clears_transform_history():
    ensure_scene_objects_registered()
    viewer, scene, _, _ = connected_viewer()
    sceneobject = scene.add(Sphere(1))
    viewer.transform_objects([sceneobject], Translation.from_vector([1, 0, 0]))

    viewer.refresh_hierarchy()

    assert not viewer.undo()


def test_scene_replacement_clears_transform_history():
    viewer, scene, _, _ = connected_viewer()
    sceneobject = scene.add(Sphere(1))
    viewer.transform_objects([sceneobject], Translation.from_vector([1, 0, 0]))

    viewer.scene = ViewerScene()

    assert not viewer.undo()


def test_scene_clear_clears_transform_history():
    viewer, scene, _, _ = connected_viewer()
    sceneobject = scene.add(Sphere(1))
    viewer.transform_objects([sceneobject], Translation.from_vector([1, 0, 0]))

    scene.clear()

    assert not viewer.undo()


def test_prepare_includes_hidden_objects_and_itemless_groups():
    ensure_scene_objects_registered()
    scene = ViewerScene()
    group = scene.add_group("Group", show=False)
    child = scene.add(Sphere(1), parent=group, show=False)

    scene.prepare()

    assert tuple(scene.render_objects) == (group.guid, child.guid)
    group_render = scene.render_object(group)
    child_render = scene.render_object(child)
    assert child_render.parent is group_render

    manager = BufferManager()
    manager.add_object(group_render)
    manager.add_object(child_render)
    assert manager.objects[group_render] == 0
    assert manager.settings[manager.objects[child_render]][2][0] == 0.0


def test_refresh_hierarchy_preserves_surviving_selection_order():
    viewer, scene, renderer, sidebar = connected_viewer(running=True)
    first = scene.add(Sphere(1))
    removed = scene.add(Sphere(1))
    last = scene.add(Sphere(1))
    viewer.state.selection.add(first, removed, last)
    scene._remove(removed, rebuild_buffers=False, cleanup_selection=False)
    renderer.reset_mock()
    sidebar.update.reset_mock()

    viewer.refresh_hierarchy()

    assert viewer.state.selection.objects == (first, last)
    renderer.rebuild_buffers.assert_called_once_with()
    sidebar.update.assert_called_once_with()
    renderer.update.assert_called_once_with()
