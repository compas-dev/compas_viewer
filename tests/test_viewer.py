from types import SimpleNamespace

import pytest

from compas_viewer import Viewer
from compas_viewer.animation import ANIMATION_PRESETS
from compas_viewer import viewer as viewer_module


class FakeImage:
    def __init__(self):
        self.saved_to = None

    def save(self, filepath):
        self.saved_to = filepath
        return True

    def width(self):
        return 640

    def height(self):
        return 360

    def scaled(self, width, height):
        return self


class FakePillowImage:
    def __init__(self):
        self.saved = None

    def convert(self, mode):
        return self

    def quantize(self, colors):
        return self

    def save(self, filepath, **kwargs):
        self.saved = (filepath, kwargs)


class FakeRenderer:
    def __init__(self):
        self.image = FakeImage()
        self.minimum = object()
        self.maximum = object()
        self.fixed_size = None
        self.updated = False

    def minimumSize(self):
        return self.minimum

    def maximumSize(self):
        return self.maximum

    def setFixedSize(self, width, height):
        self.fixed_size = (width, height)

    def setMinimumSize(self, size):
        assert size is self.minimum

    def setMaximumSize(self, size):
        assert size is self.maximum

    def update(self):
        self.updated = True

    def grabFramebuffer(self):
        return self.image


class FakeWindow:
    def __init__(self):
        self.attributes = []
        self.visible = False
        self.size = None

    def setAttribute(self, attribute, enabled):
        self.attributes.append((attribute, enabled))

    def resize(self, width, height):
        self.size = (width, height)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False


def test_save_image_renders_without_starting_event_loop(tmp_path):
    renderer = FakeRenderer()
    window = FakeWindow()
    app = SimpleNamespace(processEvents=lambda: None)
    viewer = SimpleNamespace(
        config=SimpleNamespace(window=SimpleNamespace(width=640, height=480)),
        renderer=renderer,
        ui=SimpleNamespace(window=SimpleNamespace(widget=window)),
        app=app,
        running=False,
    )
    filepath = tmp_path / "scene.png"

    result = Viewer.save_image(viewer, filepath)

    assert result == filepath
    assert renderer.fixed_size == (640, 480)
    assert renderer.updated
    assert renderer.image.saved_to == str(filepath)
    assert not viewer.running
    assert not window.visible
    assert window.attributes[0][1] is True
    assert window.attributes[-1][1] is False


@pytest.mark.parametrize(("width", "height"), [(0, 100), (100, 0), (-1, 100)])
def test_save_image_rejects_invalid_dimensions(tmp_path, width, height):
    viewer = SimpleNamespace(config=SimpleNamespace(window=SimpleNamespace(width=640, height=480)))

    with pytest.raises(ValueError, match="positive"):
        Viewer.save_image(viewer, tmp_path / "scene.png", width=width, height=height)


def test_record_animation_uses_preset_and_updates_every_frame(tmp_path, monkeypatch):
    renderer = FakeRenderer()
    window = FakeWindow()
    viewer = SimpleNamespace(
        renderer=renderer,
        ui=SimpleNamespace(window=SimpleNamespace(widget=window)),
        app=SimpleNamespace(processEvents=lambda: None),
        running=False,
    )
    images = []

    def convert(_image):
        image = FakePillowImage()
        images.append(image)
        return image

    monkeypatch.setattr(viewer_module, "_qimage_to_pillow", convert)
    updated = []
    filepath = tmp_path / "orbit.gif"

    result = Viewer.record_animation(viewer, filepath, updated.append, frames=3, preset="preview")

    assert result == filepath
    assert updated == [0, 1, 2]
    assert renderer.fixed_size == (ANIMATION_PRESETS["preview"].width, ANIMATION_PRESETS["preview"].height)
    assert images[0].saved[0] == filepath
    assert images[0].saved[1]["duration"] == round(1000 / ANIMATION_PRESETS["preview"].fps)
    assert len(images[0].saved[1]["append_images"]) == 2
    assert not viewer.running
    assert not window.visible


@pytest.mark.parametrize("preset", ["unknown", ""])
def test_record_animation_rejects_unknown_preset(tmp_path, preset):
    viewer = SimpleNamespace()

    with pytest.raises(ValueError, match="Unknown animation preset"):
        Viewer.record_animation(viewer, tmp_path / "animation.gif", lambda frame: None, 1, preset=preset)
