from types import SimpleNamespace

import pytest

from compas_viewer import Viewer
from compas_viewer.animation import ANIMATION_PRESETS
from compas_viewer.config import Config
from compas_viewer.config import WindowConfig
from compas_viewer.components.mainwindow import MainWindow
from compas_viewer.ui import UI
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
        self.fullscreen = False
        self.size = None

    def setAttribute(self, attribute, enabled):
        self.attributes.append((attribute, enabled))

    def resize(self, width, height):
        self.size = (width, height)

    def show(self):
        self.visible = True

    def showFullScreen(self):
        self.fullscreen = True
        self.visible = True

    def hide(self):
        self.visible = False


def test_viewer_assigns_configuration_before_creating_application(monkeypatch):
    configured = Config(window=WindowConfig(title="Configured Viewer"))
    instance = object.__new__(Viewer)

    class ApplicationCreated(Exception):
        pass

    def create_app(viewer):
        assert viewer.config is configured
        raise ApplicationCreated

    monkeypatch.setattr(Viewer, "create_app", create_app)

    with pytest.raises(ApplicationCreated):
        Viewer.__init__(instance, configured)


@pytest.mark.parametrize("icon", ["relative.png", "icons/viewer.png"])
def test_viewer_rejects_relative_window_icon_before_creating_application(monkeypatch, icon):
    configured = Config(window=WindowConfig(icon=icon))
    instance = object.__new__(Viewer)
    created = False

    def create_app(_viewer):
        nonlocal created
        created = True
        raise AssertionError("application should not be created")

    monkeypatch.setattr(Viewer, "create_app", create_app)

    with pytest.raises(ValueError, match="window.icon.*absolute"):
        Viewer.__init__(instance, configured)

    assert not created


def test_viewer_rejects_missing_absolute_window_icon_before_creating_application(monkeypatch, tmp_path):
    configured = Config(window=WindowConfig(icon=str(tmp_path / "missing.png")))
    instance = object.__new__(Viewer)
    created = False

    def create_app(_viewer):
        nonlocal created
        created = True
        raise AssertionError("application should not be created")

    monkeypatch.setattr(Viewer, "create_app", create_app)

    with pytest.raises(ValueError, match="window.icon.*existing file"):
        Viewer.__init__(instance, configured)

    assert not created


def test_create_app_applies_configured_identity_and_packaged_icon(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    previous_name = app.applicationName()
    previous_display_name = app.applicationDisplayName()
    previous_icon = app.windowIcon()
    instance = object.__new__(Viewer)
    instance._config = Config(window=WindowConfig(title="Configured Viewer"))

    try:
        app = Viewer.create_app(instance)

        assert app.applicationName() == "Configured Viewer"
        assert app.applicationDisplayName() == "Configured Viewer"
        assert not app.windowIcon().isNull()
    finally:
        app.setApplicationName(previous_name)
        app.setApplicationDisplayName(previous_display_name)
        app.setWindowIcon(previous_icon)


def test_window_icon_path_accepts_existing_absolute_file():
    path = viewer_module.HERE / "assets" / "icons" / "compas_icon_white.png"
    instance = object.__new__(Viewer)
    instance._config = Config(window=WindowConfig(icon=str(path)))

    assert instance._window_icon_path() == path


def test_main_window_uses_configured_title(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    configured = SimpleNamespace(config=Config(window=WindowConfig(title="Configured Window")), app=app)
    monkeypatch.setattr(MainWindow, "viewer", property(lambda _self: configured), raising=False)

    window = MainWindow()
    try:
        assert window.title == "Configured Window"
    finally:
        window.widget.close()


def test_viewer_rejects_empty_window_title_before_creating_application(monkeypatch):
    configured = Config(window=WindowConfig(title=""))
    instance = object.__new__(Viewer)
    created = False

    def create_app(_viewer):
        nonlocal created
        created = True
        raise AssertionError("application should not be created")

    monkeypatch.setattr(Viewer, "create_app", create_app)

    with pytest.raises(ValueError, match="window.title.*non-empty"):
        Viewer.__init__(instance, configured)

    assert not created


def test_viewer_validates_complete_configuration_before_creating_application(monkeypatch):
    configured = Config(vectorsize=0.0)
    instance = object.__new__(Viewer)
    created = False

    def create_app(_viewer):
        nonlocal created
        created = True
        raise AssertionError("application should not be created")

    monkeypatch.setattr(Viewer, "create_app", create_app)

    with pytest.raises(ValueError, match="vectorsize"):
        Viewer.__init__(instance, configured)

    assert not created


def test_viewer_configuration_cannot_be_replaced():
    instance = object.__new__(Viewer)
    instance._config = Config()

    with pytest.raises(AttributeError):
        instance.config = Config()


def test_ui_applies_configured_statusbar_visibility_at_initialization(monkeypatch):
    class FakeComponent:
        def __init__(self, *args):
            self.show = None

    viewport = FakeComponent()
    viewport.sidebar = FakeComponent()
    configured = SimpleNamespace(
        config=Config(),
        state=SimpleNamespace(changed=SimpleNamespace(connect=lambda callback: None)),
    )
    configured.config.ui.statusbar.show = False

    monkeypatch.setattr(UI, "viewer", property(lambda _self: configured), raising=False)
    monkeypatch.setattr("compas_viewer.ui.MainWindow", FakeComponent)
    monkeypatch.setattr("compas_viewer.ui.MenuBar", FakeComponent)
    monkeypatch.setattr("compas_viewer.ui.ToolBar", FakeComponent)
    monkeypatch.setattr("compas_viewer.ui.StatusBar", FakeComponent)
    monkeypatch.setattr("compas_viewer.ui.SideDock", FakeComponent)
    monkeypatch.setattr("compas_viewer.ui.ViewPort", lambda *args: viewport)

    ui = UI()

    assert ui.statusbar.show is False


@pytest.mark.parametrize("fullscreen", [False, True])
def test_ui_init_applies_configured_startup_window_mode(fullscreen):
    window = FakeWindow()
    size = []
    sidebar_updates = []
    ui = SimpleNamespace(
        viewer=SimpleNamespace(config=SimpleNamespace(window=SimpleNamespace(width=900, height=600, fullscreen=fullscreen))),
        window=SimpleNamespace(widget=window, resize=lambda width, height: size.append((width, height))),
        sidebar=SimpleNamespace(update=lambda: sidebar_updates.append(True)),
    )

    UI.init(ui)

    assert size == [(900, 600)]
    assert window.visible
    assert window.fullscreen is fullscreen
    assert sidebar_updates == [True]


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
