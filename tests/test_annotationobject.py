from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import call
from uuid import uuid4

import pytest
from OpenGL import GL

from compas.colors import Color
from compas.data import json_dumps
from compas.data import json_loads
from compas.geometry import Point
from compas.geometry import Translation
from compas.geometry import Vector
from compas.scene import ArrowAnnotation
from compas.scene import ComponentAnchor
from compas.scene import DimensionStyle
from compas.scene import DistanceDimension
from compas.scene import DistanceDimensionLayout
from compas.scene import PointAnchor
from compas.scene import TextAnnotation
from compas_viewer.renderer.renderer import Renderer
from compas_viewer.dimensionlayout import resolve_dimension_layout
from compas_viewer.scene import ViewerScene
import compas_viewer.scene.annotationobject as annotation_module
from compas_viewer.scene.annotationobject import ArrowAnnotationRenderObject
from compas_viewer.scene.annotationobject import DistanceDimensionRenderObject
from compas_viewer.scene.annotationobject import TextAnnotationRenderObject
from compas_viewer.scene.annotationobject import WorldAnnotationRenderObject


def test_legacy_viewer_annotation_types_and_modules_are_removed():
    import compas_viewer.scene as viewer_scene

    assert not hasattr(viewer_scene, "Tag")
    assert not hasattr(viewer_scene, "ArrowOverlay")
    with pytest.raises(ModuleNotFoundError):
        import_module("compas_viewer.scene.tagobject")
    with pytest.raises(ModuleNotFoundError):
        import_module("compas_viewer.scene.arrowoverlayobject")


def test_canonical_annotations_roundtrip_and_use_viewer_render_helpers():
    annotations = [
        TextAnnotation("Origin", [0, 0, 0]),
        ArrowAnnotation([0, 0, 0], [1, 0, 0]),
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0]), unit="m", precision=3),
    ]
    expected_types = [TextAnnotationRenderObject, ArrowAnnotationRenderObject, DistanceDimensionRenderObject]
    scene = ViewerScene()

    for annotation, expected_type in zip(annotations, expected_types, strict=True):
        restored = json_loads(json_dumps(annotation))
        sceneobject = scene.add_annotation(restored)
        assert restored == annotation
        assert isinstance(scene.annotation_render_object(sceneobject), expected_type)


def test_annotations_are_stored_outside_the_spatial_hierarchy():
    scene = ViewerScene()
    text_entry = scene.add_annotation(TextAnnotation("A", [1, 0, 0]))
    arrow_entry = scene.add_annotation(ArrowAnnotation([0, 0, 0], [1, 0, 0]))

    assert scene.objects == []
    assert scene.annotations == (text_entry, arrow_entry)
    assert isinstance(scene.annotation_render_object(text_entry), TextAnnotationRenderObject)
    assert isinstance(scene.annotation_render_object(arrow_entry), ArrowAnnotationRenderObject)


def test_distance_dimension_resolves_fixed_mixed_and_associative_anchors():
    scene = ViewerScene()
    point = scene.add(Point(2, 3, 0))
    associative = ComponentAnchor(point.guid, "point")

    fixed = scene.annotation_render_object(scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0]))))
    mixed = scene.annotation_render_object(scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), associative)))
    associated = scene.annotation_render_object(scene.add_annotation(DistanceDimension(associative, associative)))

    assert fixed.resolved_points == (Point(0, 0, 0), Point(1, 0, 0))
    assert mixed.resolved_points == (Point(0, 0, 0), Point(2, 3, 0))
    assert associated.resolved_points == (Point(2, 3, 0), Point(2, 3, 0))


@pytest.mark.parametrize(("offset", "expected_y"), [(2.0, 2.0), (-2.0, -2.0)])
def test_distance_dimension_layout_displaces_line_without_changing_anchors_or_value(offset, expected_y):
    scene = ViewerScene()
    dimension = DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([4, 0, 0]))
    entry = scene.add_annotation(dimension, layout=DistanceDimensionLayout(offset, Vector(0, 0, 3)))
    render_object = scene.annotation_render_object(entry)

    resolution = resolve_dimension_layout(entry, scene)

    assert resolution.status == "Resolved"
    assert resolution.anchors == (Point(0, 0, 0), Point(4, 0, 0))
    assert resolution.line_points == (Point(0, expected_y, 0), Point(4, expected_y, 0))
    assert render_object.resolved_points == resolution.anchors
    assert render_object.display_points == resolution.line_points
    assert dimension.distance(scene) == 4.0


@pytest.mark.parametrize(
    ("layout", "expected"),
    [
        (DistanceDimensionLayout(), "Resolved — no displacement"),
        (DistanceDimensionLayout(1.0), "Unresolved — plane normal is missing"),
        (DistanceDimensionLayout(1.0, Vector(0, 0, 0)), "Unresolved — plane normal is zero"),
        (DistanceDimensionLayout(1.0, Vector(1, 0, 0)), "Unresolved — plane normal is parallel to dimension"),
    ],
)
def test_distance_dimension_layout_status_and_zero_line_fallback(layout, expected):
    scene = ViewerScene()
    entry = scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])), layout=layout)

    resolution = resolve_dimension_layout(entry, scene)

    assert resolution.status == expected
    assert resolution.line_points == (Point(0, 0, 0), Point(1, 0, 0))
    assert not resolution.displaced


def test_unresolved_anchor_has_no_layout_line_or_stale_fallback():
    scene = ViewerScene()
    entry = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), ComponentAnchor(uuid4(), "point")),
        layout=DistanceDimensionLayout(1.0, Vector(0, 0, 1)),
    )

    resolution = resolve_dimension_layout(entry, scene)

    assert resolution.status == "Unresolved — dimension anchor is unresolved"
    assert resolution.anchors is None
    assert resolution.line_points is None


def test_coincident_dimension_layout_reports_precedence_before_normal_validation():
    scene = ViewerScene()
    entry = scene.add_annotation(
        DistanceDimension(PointAnchor([1, 2, 3]), PointAnchor([1, 2, 3])),
        layout=DistanceDimensionLayout(1.0),
    )

    resolution = resolve_dimension_layout(entry, scene)

    assert resolution.status == "Unresolved — anchors coincide"
    assert resolution.line_points == (Point(1, 2, 3), Point(1, 2, 3))


def test_distance_dimension_formats_unit_precision_override_and_unresolved_state():
    scene = ViewerScene()
    formatted = scene.annotation_render_object(scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1.25, 0, 0]), unit="mm", precision=1)))
    overridden = scene.annotation_render_object(scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0]), label="Width")))
    missing = scene.add(Point(0, 0, 0))
    unresolved = scene.annotation_render_object(scene.add_annotation(DistanceDimension(PointAnchor([0, 0, 0]), ComponentAnchor(missing.guid, "vertex", 99))))

    assert formatted.display_label == "1.2 mm"
    assert overridden.display_label == "Width"
    assert unresolved.resolved_points is None
    assert unresolved.display_label == "Unresolved"


def test_spatial_deletion_leaves_associative_dimension_unresolved():
    scene = ViewerScene()
    point = scene.add(Point(2, 0, 0))
    entry = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), ComponentAnchor(point.guid, "point")),
    )
    render_object = scene.annotation_render_object(entry)
    assert isinstance(render_object, DistanceDimensionRenderObject)
    assert render_object.resolved_points == (Point(0, 0, 0), Point(2, 0, 0))

    scene.remove(point)

    assert scene.annotations == (entry,)
    assert render_object.resolved_points is None
    assert render_object.display_label == "Unresolved"


def test_renderer_draws_dimensions_after_depth_tested_annotations(monkeypatch):
    calls = []
    depth_state = {"function": GL.GL_LESS, "test": True, "write": True}
    first = Mock(spec=TextAnnotationRenderObject)
    second = Mock(spec=ArrowAnnotationRenderObject)
    first_dimension = Mock(spec=DistanceDimensionRenderObject)
    second_dimension = Mock(spec=DistanceDimensionRenderObject)

    def draw_annotation(name):
        assert depth_state == {"function": GL.GL_LEQUAL, "test": True, "write": True}
        calls.append(name)

    def draw_dimension(name):
        assert depth_state == {"function": GL.GL_LEQUAL, "test": False, "write": False}
        calls.append(name)

    first.draw_world_annotation.side_effect = lambda renderer, view: draw_annotation("first")
    second.draw_world_annotation.side_effect = lambda renderer, view: draw_annotation("second")
    first_dimension.draw_world_annotation.side_effect = lambda renderer, view: draw_dimension("first dimension")
    second_dimension.draw_world_annotation.side_effect = lambda renderer, view: draw_dimension("second dimension")
    renderer = SimpleNamespace(
        viewer=SimpleNamespace(scene=SimpleNamespace(annotation_render_objects={1: first_dimension, 2: first, 3: second, 4: second_dimension})),
        _set_gl_capability=lambda capability, enabled: depth_state.__setitem__("test", enabled),
    )
    monkeypatch.setattr(GL, "glGetIntegerv", lambda name: depth_state["function"])
    monkeypatch.setattr(GL, "glIsEnabled", lambda capability: depth_state["test"])
    monkeypatch.setattr(GL, "glGetBooleanv", lambda name: depth_state["write"])
    monkeypatch.setattr(GL, "glDepthFunc", lambda value: depth_state.__setitem__("function", value))
    monkeypatch.setattr(GL, "glDepthMask", lambda value: depth_state.__setitem__("write", bool(value)))
    monkeypatch.setattr(GL, "glDisable", lambda capability: depth_state.__setitem__("test", False))

    Renderer._draw_world_annotations(renderer, object())

    assert calls == ["first", "second", "first dimension", "second dimension"]
    assert depth_state == {"function": GL.GL_LESS, "test": True, "write": True}


def test_renderer_restores_depth_state_when_dimension_fails(monkeypatch):
    depth_state = {"function": GL.GL_GREATER, "test": False, "write": False}
    dimension = Mock(spec=DistanceDimensionRenderObject)
    dimension.draw_world_annotation.side_effect = RuntimeError("dimension failed")
    renderer = SimpleNamespace(
        viewer=SimpleNamespace(scene=SimpleNamespace(annotation_render_objects={1: dimension})),
        _set_gl_capability=lambda capability, enabled: depth_state.__setitem__("test", enabled),
    )
    monkeypatch.setattr(GL, "glGetIntegerv", lambda name: depth_state["function"])
    monkeypatch.setattr(GL, "glIsEnabled", lambda capability: depth_state["test"])
    monkeypatch.setattr(GL, "glGetBooleanv", lambda name: depth_state["write"])
    monkeypatch.setattr(GL, "glDepthFunc", lambda value: depth_state.__setitem__("function", value))
    monkeypatch.setattr(GL, "glDepthMask", lambda value: depth_state.__setitem__("write", bool(value)))
    monkeypatch.setattr(GL, "glDisable", lambda capability: depth_state.__setitem__("test", False))

    with pytest.raises(RuntimeError, match="dimension failed"):
        Renderer._draw_world_annotations(renderer, object())

    assert depth_state == {"function": GL.GL_GREATER, "test": False, "write": False}


def test_annotations_are_excluded_from_instance_selection_state():
    scene = ViewerScene()
    render_object = scene.annotation_render_object(scene.add_annotation(TextAnnotation("A", [0, 0, 0])))

    assert isinstance(render_object, WorldAnnotationRenderObject)
    assert scene.instance_colors == {}


@pytest.mark.parametrize(
    ("annotation", "render_type", "draws_text", "draws_arrow"),
    [
        (TextAnnotation("A", [0, 0, 0]), TextAnnotationRenderObject, True, False),
        (ArrowAnnotation([0, 0, 0], [1, 0, 0]), ArrowAnnotationRenderObject, False, True),
        (
            DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])),
            DistanceDimensionRenderObject,
            True,
            True,
        ),
    ],
)
def test_annotation_draw_helpers_receive_sidebar_selection_state(
    monkeypatch,
    annotation,
    render_type,
    draws_text,
    draws_arrow,
):
    scene = ViewerScene()
    sceneobject = scene.add_annotation(annotation)
    render_object = scene.annotation_render_object(sceneobject)
    scene.attach(SimpleNamespace(state=SimpleNamespace(annotation_selection=[sceneobject]), renderer=SimpleNamespace()))
    assert isinstance(render_object, render_type)

    render_object._text_buffer = {} if draws_text else None
    render_object._arrow_buffer = {} if draws_arrow else None
    render_object.text_aspect = 1.0
    render_object.rendered_height = 12.0
    if isinstance(render_object, DistanceDimensionRenderObject):
        render_object._label = render_object.display_label
        render_object._text_size = render_object.style.text_size

    draw_text = Mock()
    draw_arrow = Mock()
    monkeypatch.setattr(annotation_module, "_draw_text", draw_text)
    monkeypatch.setattr(annotation_module, "_draw_arrow", draw_arrow)
    renderer = SimpleNamespace(
        shader_world_text=Mock(),
        shader_world_arrow=Mock(),
        width=lambda: 640,
        height=lambda: 480,
    )

    render_object.draw_world_annotation(renderer, object())

    if draws_text:
        assert draw_text.call_args.kwargs["is_selected"] is True
    else:
        draw_text.assert_not_called()
    if draws_arrow:
        assert draw_arrow.call_args.kwargs["is_selected"] is True
    else:
        draw_arrow.assert_not_called()


def test_annotation_shader_helpers_upload_selection_uniform():
    shader = Mock()
    text_buffer = {"text_texture": 1, "positions": 2, "elements": 3, "n": 4}
    arrow_buffer = {"positions": 5, "elements": 6, "n": 9}

    annotation_module._draw_text(
        shader,
        text_buffer,
        position=Point(0, 0, 0),
        transform=Translation.from_vector([0, 0, 0]).matrix,
        color=(1.0, 1.0, 1.0),
        opacity=1.0,
        screen_space=True,
        screen_size=(640, 480),
        text_aspect=1.0,
        text_height=12.0,
        vertical_align=0,
        horizontal_align=0,
        is_selected=True,
        text_offset=(2.0, -3.0),
        background_color=(0.1, 0.2, 0.3),
        background_alpha=0.5,
        background_padding=4.0,
    )
    annotation_module._draw_arrow(
        shader,
        arrow_buffer,
        start=Point(0, 0, 0),
        end=Point(1, 0, 0),
        transform=Translation.from_vector([0, 0, 0]).matrix,
        color=(1.0, 1.0, 1.0),
        opacity=1.0,
        screen_size=(640, 480),
        is_selected=True,
        line_width=3.0,
        arrow_size=12.0,
    )

    assert shader.uniform1f.call_args_list.count(call("is_selected", True)) == 2
    assert call("text_offset", (2.0, 3.0)) in shader.uniform2f.call_args_list
    assert call("background_color", (0.1, 0.2, 0.3)) in shader.uniform3f.call_args_list
    assert call("background_alpha", 0.5) in shader.uniform1f.call_args_list
    assert call("background_padding", 4.0) in shader.uniform1f.call_args_list


def test_dimension_style_reaches_draw_helpers_and_offsets_label(monkeypatch):
    scene = ViewerScene()
    entry = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([4, 0, 0])),
        style=DimensionStyle(
            color=Color.red(),
            line_width=5.0,
            extension_line_width=1.5,
            text_size=18.0,
            arrow_size=20.0,
            label_offset=7.0,
        ),
    )
    render_object = scene.annotation_render_object(entry)
    assert isinstance(render_object, DistanceDimensionRenderObject)
    scene.attach(SimpleNamespace(state=SimpleNamespace(annotation_selection=[]), renderer=SimpleNamespace()))
    render_object._arrow_buffer = {}
    render_object._text_buffer = {}
    render_object._label = render_object.display_label
    render_object._text_size = 18.0
    render_object.text_aspect = 1.0
    render_object.rendered_height = 18.0
    draw_text = Mock()
    draw_arrow = Mock()
    monkeypatch.setattr(annotation_module, "_draw_text", draw_text)
    monkeypatch.setattr(annotation_module, "_draw_arrow", draw_arrow)
    renderer = SimpleNamespace(
        shader_world_text=Mock(),
        shader_world_arrow=Mock(),
        width=lambda: 640,
        height=lambda: 480,
        project_point=lambda point: SimpleNamespace(x=point.x, y=point.y),
    )

    render_object.draw_world_annotation(renderer, object())

    assert draw_arrow.call_count == 1
    assert draw_arrow.call_args.kwargs["color"] == Color.red().rgb
    assert draw_arrow.call_args.kwargs["line_width"] == 5.0
    assert draw_arrow.call_args.kwargs["arrow_size"] == 20.0
    assert draw_text.call_args.kwargs["text_height"] == 18.0
    assert draw_text.call_args.kwargs["text_offset"] == (0.0, -7.0)


def test_displaced_dimension_draws_line_and_extensions_and_expands_bounds(monkeypatch):
    scene = ViewerScene()
    entry = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([4, 0, 0])),
        layout=DistanceDimensionLayout(2.0, Vector(0, 0, 1)),
        style=DimensionStyle(line_width=3.0, extension_line_width=1.0),
    )
    render_object = scene.annotation_render_object(entry)
    scene.attach(SimpleNamespace(state=SimpleNamespace(annotation_selection=[]), renderer=SimpleNamespace()))
    render_object._arrow_buffer = {}
    render_object._text_buffer = {}
    render_object._label = render_object.display_label
    render_object._text_size = render_object.style.text_size
    render_object.text_aspect = 1.0
    render_object.rendered_height = render_object.style.text_size
    draw_arrow = Mock()
    monkeypatch.setattr(annotation_module, "_draw_arrow", draw_arrow)
    monkeypatch.setattr(annotation_module, "_draw_text", Mock())
    renderer = SimpleNamespace(
        shader_world_text=Mock(),
        shader_world_arrow=Mock(),
        width=lambda: 640,
        height=lambda: 480,
        project_point=lambda point: SimpleNamespace(x=point.x, y=point.y),
    )

    render_object.draw_world_annotation(renderer, object())
    render_object.refresh_annotation_bounds()

    assert draw_arrow.call_count == 3
    assert draw_arrow.call_args_list[0].kwargs["start"] == Point(0, 2, 0)
    assert draw_arrow.call_args_list[0].kwargs["end"] == Point(4, 2, 0)
    assert draw_arrow.call_args_list[0].kwargs["line_width"] == 3.0
    assert [value.kwargs["line_width"] for value in draw_arrow.call_args_list[1:]] == [1.0, 1.0]
    assert [(value.kwargs["start"], value.kwargs["end"], value.kwargs["arrow_size"]) for value in draw_arrow.call_args_list[1:]] == [
        (Point(0, 0, 0), Point(0, 2, 0), 0.0),
        (Point(4, 0, 0), Point(4, 2, 0), 0.0),
    ]
    assert render_object.label_position == Point(2, 2, 0)
    assert render_object.bounding_box == [[0.0, 0.0, 0.0], [4.0, 2.0, 0.0]]


def test_default_dimension_color_reaches_arrow_and_label_draw_helpers(monkeypatch):
    scene = ViewerScene()
    entry = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([4, 0, 0])),
    )
    render_object = scene.annotation_render_object(entry)
    assert isinstance(render_object, DistanceDimensionRenderObject)
    scene.attach(SimpleNamespace(state=SimpleNamespace(annotation_selection=[]), renderer=SimpleNamespace()))
    render_object._arrow_buffer = {}
    render_object._text_buffer = {}
    render_object._label = render_object.display_label
    render_object._text_size = render_object.style.text_size
    render_object.text_aspect = 1.0
    render_object.rendered_height = render_object.style.text_size
    draw_text = Mock()
    draw_arrow = Mock()
    monkeypatch.setattr(annotation_module, "_draw_text", draw_text)
    monkeypatch.setattr(annotation_module, "_draw_arrow", draw_arrow)
    renderer = SimpleNamespace(
        shader_world_text=Mock(),
        shader_world_arrow=Mock(),
        width=lambda: 640,
        height=lambda: 480,
        project_point=lambda point: SimpleNamespace(x=point.x, y=point.y),
    )

    render_object.draw_world_annotation(renderer, object())

    assert draw_arrow.call_args.kwargs["color"] == Color.magenta().rgb
    assert draw_text.call_args.kwargs["color"] == Color.magenta().rgb


@pytest.mark.parametrize(
    ("item", "expected_color"),
    [
        (TextAnnotation("A", [0, 0, 0]), Color(0.1, 0.2, 0.3, 0.4)),
        (
            DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])),
            Color(0.4, 0.3, 0.2, 0.1),
        ),
    ],
)
def test_text_bearing_annotations_forward_label_background_to_the_text_pass(monkeypatch, item, expected_color):
    scene = ViewerScene()
    entry = scene.add_annotation(item, label_background=expected_color, label_background_padding=6.0)
    render_object = scene.annotation_render_object(entry)
    scene.attach(SimpleNamespace(state=SimpleNamespace(annotation_selection=[]), renderer=SimpleNamespace()))
    render_object._text_buffer = {}
    render_object.text_aspect = 1.0
    render_object.rendered_height = 12.0
    if isinstance(render_object, DistanceDimensionRenderObject):
        render_object._arrow_buffer = {}
        render_object._label = render_object.display_label
        render_object._text_size = render_object.style.text_size
    draw_calls = Mock()
    draw_text = draw_calls.text
    monkeypatch.setattr(annotation_module, "_draw_text", draw_text)
    monkeypatch.setattr(annotation_module, "_draw_arrow", draw_calls.arrow)
    renderer = SimpleNamespace(
        shader_world_text=Mock(),
        shader_world_arrow=Mock(),
        width=lambda: 640,
        height=lambda: 480,
        project_point=lambda point: SimpleNamespace(x=point.x, y=point.y),
    )

    render_object.draw_world_annotation(renderer, object())

    assert draw_text.call_args.kwargs["background_color"] == expected_color.rgb
    assert draw_text.call_args.kwargs["background_alpha"] == expected_color.a
    assert draw_text.call_args.kwargs["background_padding"] == 6.0
    if isinstance(render_object, DistanceDimensionRenderObject):
        assert [call_value[0] for call_value in draw_calls.method_calls] == ["arrow", "text"]


def test_default_label_background_keeps_text_pass_transparent(monkeypatch):
    scene = ViewerScene()
    render_object = scene.annotation_render_object(scene.add_annotation(TextAnnotation("A", [0, 0, 0])))
    scene.attach(SimpleNamespace(state=SimpleNamespace(annotation_selection=[]), renderer=SimpleNamespace()))
    render_object._text_buffer = {}
    render_object.text_aspect = 1.0
    render_object.rendered_height = 12.0
    draw_text = Mock()
    monkeypatch.setattr(annotation_module, "_draw_text", draw_text)
    renderer = SimpleNamespace(shader_world_text=Mock(), width=lambda: 640, height=lambda: 480)

    render_object.draw_world_annotation(renderer, object())

    assert draw_text.call_args.kwargs["background_alpha"] == 0.0
    assert draw_text.call_args.kwargs["background_padding"] == 0.0


def test_only_text_size_recreates_dimension_label_resource(monkeypatch):
    scene = ViewerScene()
    entry = scene.add_annotation(
        DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])),
    )
    render_object = scene.annotation_render_object(entry)
    assert isinstance(render_object, DistanceDimensionRenderObject)
    scene.attach(SimpleNamespace(state=SimpleNamespace(annotation_selection=[]), renderer=Mock()))
    render_object._text_buffer = {"text_texture": 1, "positions": 2, "elements": 3}
    render_object._label = render_object.display_label
    render_object._text_size = render_object.style.text_size
    make_text = Mock(return_value=({"text_texture": 4, "positions": 5, "elements": 6}, 1.0, 14.0))
    delete_text = Mock()
    monkeypatch.setattr(annotation_module, "_make_text_buffer", make_text)
    monkeypatch.setattr(annotation_module, "_delete_text_buffer", delete_text)

    render_object.style.line_width = 7.0
    render_object.update(update_data=True)

    make_text.assert_not_called()
    delete_text.assert_not_called()

    render_object.style.text_size = 14.0
    render_object.update(update_data=True)

    make_text.assert_called_once_with(render_object.display_label, 14.0)
    delete_text.assert_called_once_with({"text_texture": 1, "positions": 2, "elements": 3})
