import pytest

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Translation
from compas.scene.context import ITEM_SCENEOBJECT
from compas_viewer import plugins
from compas_viewer.scene import ArrowOverlay
from compas_viewer.scene import ArrowOverlayObject


def test_arrow_overlay_data_roundtrip():
    original = ArrowOverlay(
        (0, 0, 0),
        (1, 2, 3),
        color=Color.red(),
        linewidth=4,
        head_length=20,
        head_width=14,
        opacity=0.75,
        on_top=False,
    )

    restored = ArrowOverlay.__from_data__(original.__data__)

    assert restored.start == original.start
    assert restored.end == original.end
    assert restored.color == original.color
    assert restored.linewidth == 4
    assert restored.head_length == 20
    assert restored.head_width == 14
    assert restored.opacity == 0.75
    assert not restored.on_top


def test_arrow_overlay_transform_moves_both_anchors():
    arrow = ArrowOverlay((0, 0, 0), (1, 0, 0))

    arrow.transform(Translation.from_vector((2, 3, 4)))

    assert arrow.start == Point(2, 3, 4)
    assert arrow.end == Point(3, 3, 4)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"linewidth": 0}, "line width"),
        ({"head_length": 0}, "Arrowhead"),
        ({"head_width": -1}, "Arrowhead"),
        ({"opacity": 2}, "opacity"),
    ],
)
def test_arrow_overlay_rejects_invalid_style(kwargs, message):
    with pytest.raises(ValueError, match=message):
        ArrowOverlay((0, 0, 0), (1, 0, 0), **kwargs)


def test_arrow_overlay_rejects_zero_length_arrow():
    with pytest.raises(ValueError, match="different"):
        ArrowOverlay((0, 0, 0), (0, 0, 0))


def test_arrow_overlay_scene_object_is_registered():
    plugins.register_scene_objects()

    assert ITEM_SCENEOBJECT["Viewer"][ArrowOverlay] is ArrowOverlayObject
