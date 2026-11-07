from unittest.mock import Mock
from unittest.mock import call

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Sphere
from compas.geometry import Translation
from compas.scene import GeometryObject
from compas.scene import SceneObject
from compas_viewer.scene import ArrowOverlay
from compas_viewer.scene import Collection
from compas_viewer.scene import Tag
from compas_viewer.scene import ViewerScene
from compas_viewer.scene.arrowoverlayobject import ArrowOverlayObject
from compas_viewer.scene.tagobject import TagObject
from compas_viewer.components.objectsetting import _has_editable_face_channel


def test_standalone_viewer_scenes_keep_runtime_state_local():
    first = ViewerScene()
    second = ViewerScene()
    first_object = first.add(Sphere(1.0))
    second_object = second.add(Sphere(1.0))
    first_render = first.render_object(first_object)
    second_render = second.render_object(second_object)

    first.set_selected(first_object, True)
    first_render.init()
    second_render.init()

    assert first.is_selected(first_object)
    assert not second.is_selected(second_object)
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
        is_selected=True,
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
    assert scene.is_selected(group)
    assert shape_object.transformation is None
    assert shape_object.worldtransformation == transformation
    assert shape_object.u == 6 and shape_object.v == 4
    assert shape_object.pointcolor == Color.red()
    assert shape_object.linecolor == Color.green()
    assert shape_object.surfacecolor == Color.blue()
    assert shape_object.pointsize == 7 and shape_object.linewidth == 3
    assert not shape_object.show and scene.is_selected(shape_object)
    assert mesh_object.vertexcolor[0] == Color.red()
    assert mesh_object.edgecolor[(0, 1)] == Color.green()
    assert mesh_object.facecolor[0] == Color.blue()
    assert mesh_object.vertexsize == 7 and mesh_object.edgewidth == 3
    assert mesh_object.hide_coplanaredges and mesh_object.use_vertexcolors
    assert not mesh_object.show and scene.is_selected(mesh_object)


def test_prepare_clears_old_runtime_before_replacement(monkeypatch):
    scene = ViewerScene()
    sceneobject = scene.add(Tag("A", [0, 0, 0]))
    render_object = scene.render_object(sceneobject)
    clear = Mock()
    monkeypatch.setattr(TagObject, "clear", clear)

    scene.prepare()

    clear.assert_called_once_with(render_object)
    assert scene.render_object(sceneobject) is not render_object


def test_overlay_helpers_release_gl_resources(monkeypatch):
    import compas_viewer.scene.tagobject as tag_module

    scene = ViewerScene()
    tag = scene.render_object(scene.add(Tag("A", [0, 0, 0])))
    arrow = scene.render_object(scene.add(ArrowOverlay([0, 0, 0], [1, 0, 0])))
    assert isinstance(tag, TagObject)
    assert isinstance(arrow, ArrowOverlayObject)
    tag._text_buffer = {"text_texture": 1, "positions": 2, "elements": 3}
    arrow._arrow_buffer = {"positions": 4, "elements": 5}
    delete_textures = Mock()
    delete_buffers = Mock()
    monkeypatch.setattr(tag_module.GL, "glDeleteTextures", delete_textures)
    monkeypatch.setattr(tag_module.GL, "glDeleteBuffers", delete_buffers)

    tag.clear()
    arrow.clear()

    delete_textures.assert_called_once_with(1, [1])
    assert delete_buffers.call_args_list == [call(2, [2, 3]), call(2, [4, 5])]
    assert not hasattr(tag, "_text_buffer")
    assert not hasattr(arrow, "_arrow_buffer")


def test_remove_group_cleans_all_descendant_runtime_state():
    scene = ViewerScene()
    group = scene.add_group("Group")
    visible = scene.add(Sphere(1.0), parent=group)
    hidden = scene.add(Sphere(2.0), parent=group, show=False)
    scene.set_selected(group, True)
    scene.set_selected(visible, True)
    scene.set_selected(hidden, True)
    scene.render_object(visible).init()
    scene.render_objects[hidden.guid] = scene.render_object(hidden)

    scene.remove(group, rebuild_buffers=False)

    assert group not in scene.objects
    assert visible not in scene.objects
    assert hidden not in scene.objects
    assert not {group.guid, visible.guid, hidden.guid} & scene.render_objects.keys()
    assert not scene._selected
    assert not scene.instance_colors


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


def test_graph_inspector_does_not_expose_faces_toggle():
    from compas.datastructures import Graph

    graph = Graph()
    graph.add_node(0, x=0, y=0, z=0)
    scene = ViewerScene()
    render_object = scene.render_object(scene.add(graph))

    assert render_object.show_faces is False
    assert not _has_editable_face_channel(render_object)
