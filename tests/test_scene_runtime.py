from unittest.mock import Mock
from unittest.mock import call
from types import SimpleNamespace

import pytest

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Sphere
from compas.geometry import Translation
from compas.scene import GeometryObject
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import SceneObject
from compas.scene import ArrowAnnotation
from compas.scene import TextAnnotation
from compas_viewer import Viewer
from compas_viewer.commands import clear_scene
from compas_viewer.commands import delete_selected
from compas_viewer.components.annotationpanel import AnnotationPanel
from compas_viewer.scene import Collection
from compas_viewer.scene import ViewerScene
from compas_viewer.scene.annotationobject import ArrowAnnotationRenderObject
from compas_viewer.scene.annotationobject import TextAnnotationRenderObject
from compas_viewer.config import Config
from compas_viewer.renderer import Renderer
from compas_viewer.state import ViewerState


def connected_viewer(scene):
    events = Mock()
    renderer = SimpleNamespace(
        rebuild_buffers=events.rebuild_buffers,
        update=events.renderer_update,
        makeCurrent=events.make_current,
        doneCurrent=events.done_current,
    )
    sidebar = SimpleNamespace(
        update=events.sidebar_update,
        update_spatial_selection=events.sidebar_update,
        update_annotation_selection=events.sidebar_update,
    )
    viewer = object.__new__(Viewer)
    viewer._config = Config()
    viewer._scene = scene
    viewer.running = False
    viewer.ui = SimpleNamespace(
        viewport=SimpleNamespace(renderer=renderer),
        sidebar=sidebar,
    )
    viewer.state = ViewerState(viewer.config, scene.object, scene.annotation)
    viewer.state.changed.connect(viewer._on_state_changed)
    scene.attach(viewer)
    return viewer, events


def rebuild_renderer(*, running=True, create_buffers=None):
    events = []
    render_object = SimpleNamespace(
        _inited=False,
        init=lambda: events.append("init"),
    )
    scene = SimpleNamespace(
        prepare=lambda: events.append("prepare"),
        render_objects={"object": render_object},
        annotation_render_objects={},
    )
    manager = SimpleNamespace(
        clear=lambda: events.append("clear"),
        add_object=lambda obj: events.append(("add", obj)),
        create_buffers=create_buffers or (lambda: events.append("create")),
    )
    renderer = SimpleNamespace(
        viewer=SimpleNamespace(running=running, scene=scene),
        makeCurrent=lambda: events.append("make-current"),
        doneCurrent=lambda: events.append("done-current"),
        buffer_manager=manager,
        _vao=17,
    )
    return renderer, render_object, events


def test_rebuild_buffers_owns_gl_context_while_viewer_is_running(monkeypatch):
    import compas_viewer.renderer.renderer as renderer_module

    renderer, render_object, events = rebuild_renderer()
    monkeypatch.setattr(renderer_module.GL, "glBindVertexArray", lambda value: events.append(("bind", value)))

    Renderer.rebuild_buffers(renderer)

    assert events == [
        "make-current",
        ("bind", 17),
        "clear",
        "prepare",
        "init",
        ("add", render_object),
        "create",
        ("bind", 0),
        "done-current",
    ]


def test_rebuild_buffers_initializes_annotations_without_buffering_them(monkeypatch):
    import compas_viewer.renderer.renderer as renderer_module

    renderer, spatial, events = rebuild_renderer(running=False)
    annotation = SimpleNamespace(_inited=False, init=lambda: events.append("annotation-init"))
    renderer.viewer.scene.annotation_render_objects["annotation"] = annotation
    monkeypatch.setattr(renderer_module.GL, "glBindVertexArray", lambda value: events.append(("bind", value)))

    Renderer.rebuild_buffers(renderer)

    assert "annotation-init" in events
    assert ("add", spatial) in events
    assert ("add", annotation) not in events


def test_rebuild_buffers_balances_context_and_vertex_array_after_failure(monkeypatch):
    import compas_viewer.renderer.renderer as renderer_module

    def fail():
        events.append("create")
        raise RuntimeError("buffer creation failed")

    renderer, _render_object, events = rebuild_renderer(create_buffers=fail)
    monkeypatch.setattr(renderer_module.GL, "glBindVertexArray", lambda value: events.append(("bind", value)))

    with pytest.raises(RuntimeError, match="buffer creation failed"):
        Renderer.rebuild_buffers(renderer)

    assert events[-2:] == [("bind", 0), "done-current"]


def test_rebuild_buffers_preserves_pre_running_current_context(monkeypatch):
    import compas_viewer.renderer.renderer as renderer_module

    renderer, _render_object, events = rebuild_renderer(running=False)
    monkeypatch.setattr(renderer_module.GL, "glBindVertexArray", lambda value: events.append(("bind", value)))

    Renderer.rebuild_buffers(renderer)

    assert "make-current" not in events
    assert "done-current" not in events
    assert events[0] == ("bind", 17)
    assert events[-1] == ("bind", 0)


def test_standalone_viewer_scenes_keep_picking_state_local():
    first = ViewerScene()
    second = ViewerScene()
    first_object = first.add(Sphere(1.0))
    second_object = second.add(Sphere(1.0))
    first_render = first.render_object(first_object)
    second_render = second.render_object(second_object)

    first_render.init()
    second_render.init()

    assert not first_render.is_selected
    assert not second_render.is_selected
    assert first_render.runtime_scene is first
    assert second_render.runtime_scene is second
    assert set(first.instance_colors.values()) == {first_object}
    assert set(second.instance_colors.values()) == {second_object}


def test_collection_expands_with_explicit_presentation_and_group_transform():
    scene = ViewerScene()
    mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])
    collection = Collection([Sphere(1.0), mesh])
    transformation = Translation.from_vector([2, 3, 4])

    group = scene.add(
        collection,
        name="Parts",
        show=False,
        pointcolor=Color.red(),
        linecolor=Color.green(),
        facecolor=Color.blue(),
        pointsize=7,
        linewidth=3,
        opacity=0.5,
        hide_coplanaredges=True,
        use_vertexcolors=True,
        u=6,
        v=4,
        transformation=transformation,
    )
    shape_object, mesh_object = group.children

    assert group.name == "Parts"
    assert group.transformation == transformation
    assert group.opacity == 0.5
    assert not group.show
    assert shape_object.transformation is None
    assert shape_object.worldtransformation == transformation
    assert shape_object.u == 6 and shape_object.v == 4
    assert shape_object.pointcolor == Color.red()
    assert shape_object.linecolor == Color.green()
    assert shape_object.surfacecolor == Color.blue()
    assert shape_object.pointsize == 7 and shape_object.linewidth == 3
    assert not shape_object.show
    assert mesh_object.vertexcolor[0] == Color.red()
    assert mesh_object.edgecolor[(0, 1)] == Color.green()
    assert mesh_object.facecolor[0] == Color.blue()
    assert mesh_object.vertexsize == 7 and mesh_object.edgewidth == 3
    assert mesh_object.hide_coplanaredges and mesh_object.use_vertexcolors
    assert not mesh_object.show


def test_prepare_clears_old_runtime_before_replacement(monkeypatch):
    scene = ViewerScene()
    sceneobject = scene.add_annotation(TextAnnotation("A", [0, 0, 0]))
    render_object = scene.annotation_render_object(sceneobject)
    clear = Mock()
    monkeypatch.setattr(TextAnnotationRenderObject, "clear", clear)

    scene.prepare()

    clear.assert_called_once_with(render_object)
    assert scene.annotation_render_object(sceneobject) is not render_object


def test_annotation_helpers_release_gl_resources(monkeypatch):
    import compas_viewer.scene.annotationobject as annotation_module

    scene = ViewerScene()
    text = scene.annotation_render_object(scene.add_annotation(TextAnnotation("A", [0, 0, 0])))
    arrow = scene.annotation_render_object(scene.add_annotation(ArrowAnnotation([0, 0, 0], [1, 0, 0])))
    assert isinstance(text, TextAnnotationRenderObject)
    assert isinstance(arrow, ArrowAnnotationRenderObject)
    text._text_buffer = {"text_texture": 1, "positions": 2, "elements": 3}
    arrow._arrow_buffer = {"positions": 4, "elements": 5}
    delete_textures = Mock()
    delete_buffers = Mock()
    monkeypatch.setattr(annotation_module.GL, "glDeleteTextures", delete_textures)
    monkeypatch.setattr(annotation_module.GL, "glDeleteBuffers", delete_buffers)

    text.clear()
    arrow.clear()

    delete_textures.assert_called_once_with(1, [1])
    assert delete_buffers.call_args_list == [call(2, [2, 3]), call(2, [4, 5])]
    assert not hasattr(text, "_text_buffer")
    assert not hasattr(arrow, "_arrow_buffer")


def test_annotation_refresh_does_not_rebuild_spatial_buffers():
    scene = ViewerScene()
    viewer, events = connected_viewer(scene)
    annotation = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])),
    )
    render_object = Mock(_inited=True)
    scene.annotation_render_objects[annotation.guid] = render_object
    viewer.running = True

    viewer.refresh_annotations((annotation,))

    render_object.update.assert_called_once_with(update_data=True)
    events.rebuild_buffers.assert_not_called()
    assert events.make_current.call_count == 1
    assert events.done_current.call_count == 1


def test_remove_group_cleans_all_descendant_runtime_state():
    scene = ViewerScene()
    state = ViewerState(Config(), scene.object)
    scene.attach(SimpleNamespace(state=state, running=False))
    group = scene.add_group("Group")
    visible = scene.add(Sphere(1.0), parent=group)
    hidden = scene.add(Sphere(2.0), parent=group, show=False)
    state.selection.add(group, visible, hidden)
    changes = []
    state.changed.connect(lambda path, value: changes.append((path, value)))
    scene.render_object(visible).init()
    scene.render_objects[hidden.guid] = scene.render_object(hidden)

    scene.remove(group, rebuild_buffers=False)

    assert group not in scene.objects
    assert visible not in scene.objects
    assert hidden not in scene.objects
    assert not {group.guid, visible.guid, hidden.guid} & scene.render_objects.keys()
    assert not state.selection
    assert not scene.instance_colors
    assert changes == [("selection", ())]


def test_direct_clear_with_selection_syncs_once_after_scene_and_buffers():
    scene = ViewerScene()
    viewer, events = connected_viewer(scene)
    first = scene.add(Sphere(1.0))
    second = scene.add(Sphere(2.0))
    scene.render_objects[first.guid] = scene.render_object(first)
    scene.instance_colors[(1, 2, 3)] = first
    viewer.state.selection.add(first, second)
    events.reset_mock()
    viewer.running = True

    scene.clear()

    assert not scene.objects
    assert not scene.render_objects
    assert not scene.instance_colors
    assert not viewer.state.selection
    assert events.mock_calls == [
        call.make_current(),
        call.done_current(),
        call.rebuild_buffers(),
        call.sidebar_update(),
        call.renderer_update(),
    ]


def test_direct_clear_without_selection_syncs_once_after_scene_and_buffers():
    scene = ViewerScene()
    viewer, events = connected_viewer(scene)
    sceneobject = scene.add(Sphere(1.0))
    scene.render_objects[sceneobject.guid] = scene.render_object(sceneobject)
    scene.instance_colors[(1, 2, 3)] = sceneobject
    events.reset_mock()
    viewer.running = True

    scene.clear()

    assert not scene.objects
    assert not scene.render_objects
    assert not scene.instance_colors
    assert not viewer.state.selection
    assert events.mock_calls == [
        call.make_current(),
        call.done_current(),
        call.rebuild_buffers(),
        call.sidebar_update(),
        call.renderer_update(),
    ]


def test_direct_clear_removes_entries_before_resolver_sensitive_sidebar_refresh(monkeypatch):
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    scene = ViewerScene()
    viewer, _events = connected_viewer(scene)
    spatial = scene.add(Sphere(1.0))
    annotation = scene.add_annotation(TextAnnotation("A", [0, 0, 0]))
    scene.annotation_render_object(annotation)
    viewer.state.selection.add(spatial)
    viewer.state.annotation_selection.add(annotation)
    monkeypatch.setattr(AnnotationPanel, "viewer", property(lambda _self: viewer), raising=False)
    panel = AnnotationPanel()
    viewer.ui.sidebar = SimpleNamespace(
        update=panel.update,
        update_spatial_selection=lambda: None,
        update_annotation_selection=panel.update,
    )
    panel.update()

    scene.clear()

    assert scene.annotations == ()
    assert scene.annotation_render_objects == {}
    assert not viewer.state.selection
    assert not viewer.state.annotation_selection
    assert panel.tree.topLevelItemCount() == 0
    assert app is not None


@pytest.mark.parametrize(("clear_scene", "clear_context"), [(False, True), (True, False)])
def test_clear_owns_and_balances_gl_context_for_annotation_cleanup(clear_scene, clear_context):
    scene = ViewerScene()
    viewer, events = connected_viewer(scene)
    annotation = scene.add_annotation(TextAnnotation("A", [0, 0, 0]))
    scene.annotation_render_object(annotation)

    class AnnotationResource:
        def clear(self):
            assert events.make_current.call_count == 1
            assert events.done_current.call_count == 0

    scene.annotation_render_objects[annotation.guid] = AnnotationResource()
    viewer.running = True

    scene.clear(clear_scene=clear_scene, clear_context=clear_context)

    assert events.make_current.call_count == 1
    assert events.done_current.call_count == 1


def test_clear_context_balances_gl_context_when_annotation_cleanup_fails():
    scene = ViewerScene()
    viewer, events = connected_viewer(scene)
    annotation = scene.add_annotation(TextAnnotation("A", [0, 0, 0]))
    scene.annotation_render_object(annotation)

    class FailingAnnotationResource:
        def clear(self):
            raise RuntimeError("cleanup failed")

    scene.annotation_render_objects[annotation.guid] = FailingAnnotationResource()
    viewer.running = True

    with pytest.raises(RuntimeError, match="cleanup failed"):
        scene.clear(clear_scene=False, clear_context=True)

    assert events.make_current.call_count == 1
    assert events.done_current.call_count == 1


def test_delete_selected_batches_parent_and_descendant_selection():
    scene = ViewerScene()
    viewer, events = connected_viewer(scene)
    group = scene.add_group("Group")
    child = scene.add(Sphere(1.0), parent=group)
    viewer.state.selection.add(group, child)
    events.reset_mock()
    viewer.running = True

    delete_selected(viewer)

    assert not scene.objects
    assert not viewer.state.selection
    assert events.mock_calls == [
        call.make_current(),
        call.done_current(),
        call.rebuild_buffers(),
        call.sidebar_update(),
        call.renderer_update(),
    ]


def test_clear_scene_command_uses_one_post_mutation_sync():
    scene = ViewerScene()
    viewer, events = connected_viewer(scene)
    sceneobject = scene.add(Sphere(1.0))
    viewer.state.selection.add(sceneobject)
    events.reset_mock()
    viewer.running = True

    clear_scene(viewer)

    assert not scene.objects
    assert not viewer.state.selection
    assert events.mock_calls == [
        call.make_current(),
        call.done_current(),
        call.rebuild_buffers(),
        call.sidebar_update(),
        call.renderer_update(),
    ]


def test_delete_selected_balances_gl_context_when_resource_cleanup_fails():
    scene = ViewerScene()
    viewer, events = connected_viewer(scene)
    sceneobject = scene.add(Sphere(1.0))
    scene.render_object(sceneobject)

    class FailingSpatialResource:
        def clear(self):
            raise RuntimeError("cleanup failed")

    scene.render_objects[sceneobject.guid] = FailingSpatialResource()
    viewer.state.selection.add(sceneobject)
    events.reset_mock()
    viewer.running = True

    with pytest.raises(RuntimeError, match="cleanup failed"):
        delete_selected(viewer)

    assert events.mock_calls == [call.make_current(), call.done_current()]


def test_operation_registration_coexists_with_specialized_viewer_operation():
    from compas.scene.context import SCENE_OPERATIONS
    from compas_viewer import plugins

    previous = SCENE_OPERATIONS.get("Viewer")

    def specialized(*args):
        return []

    SCENE_OPERATIONS["Viewer"] = {GeometryObject: {"draw": specialized}}
    try:
        plugins.ensure_scene_objects_registered()
        assert SCENE_OPERATIONS["Viewer"][GeometryObject]["draw"] is specialized
        assert set(SCENE_OPERATIONS["Viewer"][SceneObject]) == {"draw", "clear"}
    finally:
        if previous is None:
            SCENE_OPERATIONS.pop("Viewer", None)
        else:
            SCENE_OPERATIONS["Viewer"] = previous
