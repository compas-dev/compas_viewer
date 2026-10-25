import pytest
from types import SimpleNamespace

from compas.colors import Color
from compas.geometry import Point
from compas.geometry import Translation
from compas_viewer.scene import Tag
from compas_viewer.scene.tagobject import GL
from compas_viewer.scene.tagobject import TagObject


def test_tag_supports_multiline_annotation_styling():
    tag = Tag(
        "Node A\nElevation +3.20",
        Point(1, 2, 3),
        color=Color.white(),
        height=18,
        horizontal_align="center",
        vertical_align="top",
        backgroundcolor=Color(0, 0, 0, 0.75),
        padding=4,
        offset=(0, 8),
        line_spacing=1.2,
    )

    assert tag.text.splitlines() == ["Node A", "Elevation +3.20"]
    assert tag.position == Point(1, 2, 3)
    assert tag.horizontal_align == "center"
    assert tag.vertical_align == "top"
    assert tag.backgroundcolor == Color(0, 0, 0, 0.75)
    assert tag.padding == 4
    assert tag.offset == (0, 8)


def test_tag_data_roundtrip_preserves_annotation_settings():
    original = Tag("A", (1, 2, 3), height=20, absolute_height=True, padding=2, offset=(3, 4))

    restored = Tag.__from_data__(original.__data__)

    assert restored == original


def test_tag_transform_moves_anchor():
    tag = Tag("A", (1, 2, 3))

    tag.transform(Translation.from_vector((4, 5, 6)))

    assert tag.position == Point(5, 7, 9)


def test_multiline_text_rasterization_increases_texture_height(monkeypatch):
    uploaded = []
    monkeypatch.setattr(GL, "glGenTextures", lambda count: 1)
    monkeypatch.setattr(GL, "glBindTexture", lambda *args: None)
    monkeypatch.setattr(GL, "glPixelStorei", lambda *args: None)
    monkeypatch.setattr(GL, "glTexParameteri", lambda *args: None)
    monkeypatch.setattr(GL, "glTexImage2D", lambda *args: uploaded.append(args[-1].shape))

    single = SimpleNamespace(geometry=Tag("First", (0, 0, 0), height=20, padding=2))
    multiline = SimpleNamespace(geometry=Tag("First\nSecond", (0, 0, 0), height=20, padding=2))

    TagObject.make_text_texture(single)
    TagObject.make_text_texture(multiline)

    assert uploaded[1][0] > uploaded[0][0]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"height": 0}, "height"),
        ({"padding": -1}, "padding"),
        ({"line_spacing": 0}, "line spacing"),
        ({"horizontal_align": "middle"}, "horizontal alignment"),
        ({"vertical_align": "baseline"}, "vertical alignment"),
    ],
)
def test_tag_rejects_invalid_annotation_settings(kwargs, message):
    with pytest.raises(ValueError, match=message):
        Tag("A", (0, 0, 0), **kwargs)
