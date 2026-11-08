from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import call

import pytest

from compas.data import json_dumps
from compas.data import json_loads
from compas.geometry import Point
from compas.geometry import Translation
from compas.scene import ArrowAnnotation
from compas.scene import ComponentAnchor
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import TextAnnotation
from compas_viewer.renderer.renderer import Renderer
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
        sceneobject = scene.add(restored)
        assert restored == annotation
        assert isinstance(scene.render_object(sceneobject), expected_type)


def test_annotation_helpers_apply_parent_world_transformation():
    scene = ViewerScene()
    group = scene.add_group("Annotations", transformation=Translation.from_vector([2, 3, 4]))
    text = scene.render_object(scene.add(TextAnnotation("A", [1, 0, 0]), parent=group))
    arrow = scene.render_object(scene.add(ArrowAnnotation([0, 0, 0], [1, 0, 0]), parent=group))

    assert Point(1, 0, 0).transformed(text.worldtransformation) == Point(3, 3, 4)
    assert Point(1, 0, 0).transformed(arrow.worldtransformation) == Point(3, 3, 4)


def test_distance_dimension_resolves_fixed_mixed_and_associative_anchors():
    scene = ViewerScene()
    group = scene.add_group("Dimensions", transformation=Translation.from_vector([10, 0, 0]))
    point = scene.add(Point(2, 0, 0), transformation=Translation.from_vector([0, 3, 0]))
    associative = ComponentAnchor(point.guid, "point")

    fixed = scene.render_object(scene.add(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0])), parent=group))
    mixed = scene.render_object(scene.add(DistanceDimension(PointAnchor([0, 0, 0]), associative), parent=group))
    associated = scene.render_object(scene.add(DistanceDimension(associative, associative), parent=group))

    assert fixed.resolved_points == (Point(10, 0, 0), Point(11, 0, 0))
    assert mixed.resolved_points == (Point(10, 0, 0), Point(2, 3, 0))
    assert associated.resolved_points == (Point(2, 3, 0), Point(2, 3, 0))


def test_distance_dimension_formats_unit_precision_override_and_unresolved_state():
    scene = ViewerScene()
    formatted = scene.render_object(scene.add(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1.25, 0, 0]), unit="mm", precision=1)))
    overridden = scene.render_object(scene.add(DistanceDimension(PointAnchor([0, 0, 0]), PointAnchor([1, 0, 0]), label="Width")))
    missing = scene.add(Point(0, 0, 0))
    unresolved = scene.render_object(scene.add(DistanceDimension(PointAnchor([0, 0, 0]), ComponentAnchor(missing.guid, "vertex", 99))))

    assert formatted.display_label == "1.2 mm"
    assert overridden.display_label == "Width"
    assert unresolved.resolved_points is None
    assert unresolved.display_label == "Unresolved"


def test_renderer_draws_world_annotations_once_in_scene_order():
    calls = []
    first = Mock(spec=WorldAnnotationRenderObject)
    second = Mock(spec=WorldAnnotationRenderObject)
    first.draw_world_annotation.side_effect = lambda renderer, view: calls.append("first")
    second.draw_world_annotation.side_effect = lambda renderer, view: calls.append("second")
    renderer = SimpleNamespace(viewer=SimpleNamespace(scene=SimpleNamespace(render_objects={1: first, 2: object(), 3: second})))

    Renderer._draw_world_annotations(renderer, object())

    assert calls == ["first", "second"]


def test_annotations_are_excluded_from_instance_selection_state():
    scene = ViewerScene()
    render_object = scene.render_object(scene.add(TextAnnotation("A", [0, 0, 0])))

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
    sceneobject = scene.add(annotation)
    render_object = scene.render_object(sceneobject)
    scene.attach(SimpleNamespace(state=SimpleNamespace(selection=[sceneobject]), renderer=SimpleNamespace()))
    assert isinstance(render_object, render_type)

    render_object._text_buffer = {} if draws_text else None
    render_object._arrow_buffer = {} if draws_arrow else None
    render_object.text_aspect = 1.0
    render_object.rendered_height = 12.0
    if isinstance(render_object, DistanceDimensionRenderObject):
        render_object._label = render_object.display_label

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
    )

    assert shader.uniform1f.call_args_list.count(call("is_selected", True)) == 2
