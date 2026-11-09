from importlib import import_module
from math import isclose
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from typing import cast
from typing import Literal
from unittest.mock import Mock

import pytest

from compas.colors import Color
from compas_viewer import LegendOverlay
from compas_viewer import ScaleBarOverlay
from compas_viewer import ScreenTextOverlay
from compas_viewer import Viewer
from compas_viewer.overlays import Overlay
from compas_viewer.overlays import _OverlayContext
from compas_viewer.overlays import _OverlayLayer
from compas_viewer.renderer import Renderer
from compas_viewer.scene import ViewerScene


ROOT = Path(__file__).parents[1]


def test_overlay_layer_preserves_insertion_order_and_removes_by_identity():
    layer = _OverlayLayer()
    scale = ScaleBarOverlay()
    legend = LegendOverlay([("Structure", Color.red()), ("Context", Color.grey())], title="Objects")
    text = ScreenTextOverlay("Origin", (0.0, 0.0))

    layer.add(scale)
    layer.add(legend)
    layer.add(text)

    assert tuple(layer) == (scale, legend, text)
    assert layer.remove(scale)
    assert tuple(layer) == (legend, text)
    assert not layer.remove(scale)


def test_overlay_layer_rejects_duplicates_and_unapproved_types():
    layer = _OverlayLayer()
    scale = ScaleBarOverlay()
    layer.add(scale)

    with pytest.raises(ValueError, match="already present"):
        layer.add(scale)
    with pytest.raises(TypeError, match="ScaleBarOverlay, LegendOverlay, or ScreenTextOverlay"):
        layer.add(cast(Overlay, object()))


@pytest.mark.parametrize(
    ("kwargs", "error", "message"),
    [
        ({"text": cast(str, object())}, TypeError, "content.*string"),
        ({"position": cast(tuple[float, float], [0.0, 0.0])}, TypeError, "position.*pair"),
        ({"position": (True, 0.0)}, TypeError, "coordinates.*non-boolean numbers"),
        ({"position": (float("nan"), 0.0)}, ValueError, "coordinates.*finite"),
        ({"position": (float("inf"), 0.0)}, ValueError, "coordinates.*finite"),
        ({"position": (-0.1, 0.0)}, ValueError, "coordinates.*between zero and one"),
        ({"position": (0.0, 1.1)}, ValueError, "coordinates.*between zero and one"),
        ({"horizontal_alignment": cast(Literal["left", "center", "right"], "middle")}, ValueError, "horizontal alignment"),
        ({"vertical_alignment": cast(Literal["top", "center", "bottom"], "middle")}, ValueError, "vertical alignment"),
        ({"color": cast(Color, object())}, TypeError, "COMPAS Color"),
    ],
)
def test_screen_text_rejects_invalid_presentation(kwargs, error, message):
    values = {"text": "Label", "position": (0.5, 0.5)}
    values.update(kwargs)
    with pytest.raises(error, match=message):
        ScreenTextOverlay(**values)


@pytest.mark.parametrize(
    ("kwargs", "error", "message"),
    [
        ({"target_pixels": True}, TypeError, "target pixels.*non-boolean number"),
        ({"target_pixels": "120"}, TypeError, "target pixels.*non-boolean number"),
        ({"target_pixels": float("nan")}, ValueError, "target pixels.*finite"),
        ({"target_pixels": float("inf")}, ValueError, "target pixels.*finite"),
        ({"target_pixels": 0}, ValueError, "target pixels.*positive"),
        ({"margin": False}, TypeError, "margin.*non-boolean number"),
        ({"margin": "20"}, TypeError, "margin.*non-boolean number"),
        ({"margin": float("nan")}, ValueError, "margin.*finite"),
        ({"margin": float("inf")}, ValueError, "margin.*finite"),
        ({"margin": -1}, ValueError, "margin.*negative"),
        ({"color": cast(Color, object())}, TypeError, "COMPAS Color"),
    ],
)
def test_scale_bar_rejects_invalid_display_settings(kwargs, error, message):
    with pytest.raises(error, match=message):
        ScaleBarOverlay(**kwargs)


@pytest.mark.parametrize(
    "context",
    [
        _OverlayContext(width=640, height=480, camera_distance=0, field_of_view=45, perspective=False),
        _OverlayContext(width=640, height=480, camera_distance=10, field_of_view=180, perspective=True),
    ],
)
def test_scale_bar_rejects_invalid_camera_values(context):
    with pytest.raises(ValueError):
        ScaleBarOverlay()._layout(context)


def test_legend_rejects_empty_entries():
    with pytest.raises(ValueError, match="at least one entry"):
        LegendOverlay([])


def test_orthographic_scale_is_global_and_responds_to_viewport_width():
    overlay = ScaleBarOverlay(target_pixels=120)
    wide = overlay._layout(
        _OverlayContext(
            width=1000,
            height=600,
            camera_distance=10,
            field_of_view=45,
            perspective=False,
            unit="m",
            precision=2,
        )
    )
    narrow = overlay._layout(
        _OverlayContext(
            width=500,
            height=600,
            camera_distance=10,
            field_of_view=45,
            perspective=False,
            unit="m",
            precision=2,
        )
    )

    assert wide.world_length == 2
    assert wide.pixel_length == 100
    assert wide.label == "2.00 m"
    assert not wide.depth_dependent
    assert narrow.world_length == 5
    assert narrow.pixel_length == 125


def test_perspective_scale_is_local_to_camera_target_depth():
    layout = ScaleBarOverlay(target_pixels=120)._layout(
        _OverlayContext(
            width=1000,
            height=600,
            camera_distance=10,
            field_of_view=90,
            perspective=True,
            unit="m",
            precision=1,
        )
    )

    assert layout.world_length == 5
    assert isclose(layout.pixel_length, 150)
    assert layout.label == "5.0 m at target depth"
    assert layout.depth_dependent


@pytest.mark.parametrize("target_pixels", [8, 40, 120, 400, 1200])
def test_scale_bar_uses_one_two_five_lengths(target_pixels):
    layout = ScaleBarOverlay(target_pixels=target_pixels)._layout(_OverlayContext(width=800, height=600, camera_distance=10, field_of_view=45, perspective=False))
    exponent = 10 ** int(f"{layout.world_length:e}".split("e")[1])

    assert layout.world_length / exponent in {1, 2, 5}


def test_legend_keeps_order_title_and_colors():
    entries = [("First", Color.red()), ("Second", Color.green()), ("Third", Color.blue())]
    legend = LegendOverlay(entries, title="Categories")

    assert legend.entries == tuple(entries)
    assert legend.title == "Categories"


def test_overlay_layer_draws_scale_and_legend(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QColor
    from PySide6.QtGui import QImage
    from PySide6.QtGui import QPainter
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    image = QImage(640, 480, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter(image)
    layer = _OverlayLayer()
    layer.add(ScaleBarOverlay())
    layer.add(LegendOverlay([("A", Color.red()), ("B", Color.blue())], title="Categories"))

    layer.draw(painter, _OverlayContext(width=640, height=480, camera_distance=10, field_of_view=45, perspective=False))
    painter.end()

    assert app is not None
    assert image.pixelColor(20, 460).alpha() > 0


def test_screen_text_uses_normalized_alignment_and_camera_independent_position(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QColor
    from PySide6.QtGui import QImage
    from PySide6.QtGui import QPainter
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    overlay = ScreenTextOverlay(
        "Viewport",
        (0.25, 0.5),
        horizontal_alignment="center",
        vertical_alignment="center",
        color=Color.white(),
    )

    def render(width, height, camera_distance):
        image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(QColor(0, 0, 0, 0))
        painter = QPainter(image)
        layer = _OverlayLayer()
        layer.add(overlay)
        layer.draw(
            painter,
            _OverlayContext(
                width=width,
                height=height,
                camera_distance=camera_distance,
                field_of_view=45,
                perspective=True,
            ),
        )
        assert painter.hasClipping()
        assert painter.clipBoundingRect().toRect() == image.rect()
        painter.end()
        return image

    def opaque_bounds(image):
        points = [(x, y) for y in range(image.height()) for x in range(image.width()) if image.pixelColor(x, y).alpha()]
        assert points
        xs, ys = zip(*points, strict=True)
        return min(xs), min(ys), max(xs), max(ys)

    small = render(200, 100, 10)
    same_viewport_different_camera = render(200, 100, 100)
    large = render(400, 200, 10)
    small_bounds = opaque_bounds(small)
    large_bounds = opaque_bounds(large)

    assert small == same_viewport_different_camera
    assert abs((small_bounds[0] + small_bounds[2]) / 2 - 50) <= 2
    assert abs((small_bounds[1] + small_bounds[3]) / 2 - 50) <= 2
    assert abs((large_bounds[0] + large_bounds[2]) / 2 - 100) <= 2
    assert abs((large_bounds[1] + large_bounds[3]) / 2 - 100) <= 2
    assert app is not None


def test_viewer_overlay_facade_does_not_change_scene_serialization():
    viewer = object.__new__(Viewer)
    viewer._overlay_layer = _OverlayLayer()
    viewer._scene = ViewerScene()
    viewer.running = False
    before = viewer.scene.__data__
    text = ScreenTextOverlay("Status", (1.0, 0.0), horizontal_alignment="right")

    viewer.add_overlay(text)

    assert viewer.overlays == (text,)
    assert viewer.scene.__data__ == before
    assert viewer.scene.objects == []
    assert viewer.remove_overlay(text)
    assert viewer.overlays == ()


def test_running_viewer_repaints_overlay_canvas_without_rendering_scene():
    viewport = SimpleNamespace(renderer=Mock(), update_overlays=Mock())
    viewer = object.__new__(Viewer)
    viewer._overlay_layer = _OverlayLayer()
    viewer.running = True
    viewer.ui = SimpleNamespace(viewport=viewport)
    scale = ScaleBarOverlay()

    viewer.add_overlay(scale)
    assert viewer.remove_overlay(scale)

    assert viewport.update_overlays.call_count == 2
    viewport.renderer.update.assert_not_called()


def test_measurement_state_repaints_overlay_canvas_without_rendering_scene():
    viewport = SimpleNamespace(renderer=Mock(), update_overlays=Mock())
    viewer = SimpleNamespace(ui=SimpleNamespace(viewport=viewport))

    Viewer._on_state_changed(viewer, "measurement.runtime", object())

    viewport.update_overlays.assert_called_once_with()
    viewport.renderer.update.assert_not_called()


def test_renderer_keeps_display_and_instance_frames_in_native_gl(monkeypatch):
    renderer_module = import_module("compas_viewer.renderer.renderer")
    order = []
    fake = SimpleNamespace(
        rendermode="shaded",
        _frames=0,
        _now=float("inf"),
        clear=lambda: order.append("clear"),
        width=lambda: 640,
        height=lambda: 480,
        devicePixelRatio=lambda: 2,
        paint=lambda is_instance=False: order.append(("paint", is_instance)),
    )
    monkeypatch.setattr(renderer_module.GL, "glViewport", lambda *args: order.append(("viewport", args)))

    Renderer.paintGL(fake)
    Renderer.paintGL(fake, is_instance=True)

    assert order == [
        "clear",
        ("viewport", (0, 0, 1280, 960)),
        ("paint", False),
        "clear",
        ("viewport", (0, 0, 640, 480)),
        ("paint", True),
    ]


def test_overlay_canvas_is_transparent_to_input_and_tracks_content(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    from compas_viewer.components.viewport import _OverlayCanvas

    app = QApplication.instance() or QApplication([])
    content = {"visible": False}
    viewer = SimpleNamespace(_has_overlay_content=lambda: content["visible"])
    monkeypatch.setattr(_OverlayCanvas, "viewer", property(lambda _self: viewer), raising=False)
    canvas = _OverlayCanvas(cast(Renderer, object()))
    update = Mock()
    monkeypatch.setattr(canvas, "update", update)

    canvas.sync()
    assert not canvas.isVisible()
    update.assert_not_called()

    content["visible"] = True
    canvas.sync()

    assert canvas.isVisible()
    update.assert_called_once_with()
    assert canvas.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    assert canvas.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    assert canvas.focusPolicy() == Qt.FocusPolicy.NoFocus
    assert app is not None


def test_overlay_canvas_owns_and_ends_painter_inside_paint_event(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    import compas_viewer.components.viewport as viewport_module
    from compas_viewer.components.viewport import _OverlayCanvas

    app = QApplication.instance() or QApplication([])
    renderer = cast(Renderer, object())
    viewer = SimpleNamespace(
        _has_overlay_content=lambda: True,
        _draw_overlays=Mock(side_effect=RuntimeError("draw failed")),
    )
    monkeypatch.setattr(_OverlayCanvas, "viewer", property(lambda _self: viewer), raising=False)
    canvas = _OverlayCanvas(renderer)
    painter = Mock()
    painter.begin.return_value = True
    monkeypatch.setattr(viewport_module, "QPainter", Mock(return_value=painter))

    with pytest.raises(RuntimeError, match="draw failed"):
        canvas.paintEvent(Mock())

    painter.begin.assert_called_once_with(canvas)
    viewer._draw_overlays.assert_called_once_with(renderer, painter)
    painter.end.assert_called_once_with()
    assert app is not None


def test_overlay_canvas_skips_drawing_when_painter_cannot_begin(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    import compas_viewer.components.viewport as viewport_module
    from compas_viewer.components.viewport import _OverlayCanvas

    app = QApplication.instance() or QApplication([])
    viewer = SimpleNamespace(_has_overlay_content=lambda: True, _draw_overlays=Mock())
    monkeypatch.setattr(_OverlayCanvas, "viewer", property(lambda _self: viewer), raising=False)
    canvas = _OverlayCanvas(cast(Renderer, object()))
    painter = Mock()
    painter.begin.return_value = False
    monkeypatch.setattr(viewport_module, "QPainter", Mock(return_value=painter))

    canvas.paintEvent(Mock())

    viewer._draw_overlays.assert_not_called()
    painter.end.assert_not_called()
    assert app is not None


def test_viewport_stacks_overlay_above_renderer_and_repaints_after_frame(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from PySide6.QtWidgets import QMainWindow
    from PySide6.QtWidgets import QStackedLayout
    from PySide6.QtWidgets import QWidget

    import compas_viewer.components.viewport as viewport_module

    class Signal:
        def __init__(self):
            self.callback = None

        def connect(self, callback):
            self.callback = callback

        def emit(self):
            assert self.callback is not None
            self.callback()

    class FakeRenderer(QWidget):
        def __init__(self):
            super().__init__()
            self.frameSwapped = Signal()

    class FakeSidebar:
        def __init__(self, _viewport):
            self.widget = QWidget()

    app = QApplication.instance() or QApplication([])
    content = {"visible": False}
    viewer = SimpleNamespace(
        config=SimpleNamespace(
            ui=SimpleNamespace(sidebar=SimpleNamespace(width=200)),
            window=SimpleNamespace(width=800),
        ),
        _has_overlay_content=lambda: content["visible"],
    )
    monkeypatch.setattr(viewport_module, "Renderer", FakeRenderer)
    monkeypatch.setattr(viewport_module, "SideBarRight", FakeSidebar)
    monkeypatch.setattr(viewport_module.ViewPort, "viewer", property(lambda _self: viewer), raising=False)
    monkeypatch.setattr(viewport_module._OverlayCanvas, "viewer", property(lambda _self: viewer), raising=False)
    window = SimpleNamespace(widget=QMainWindow())

    viewport = viewport_module.ViewPort(window)

    assert viewport.widget.widget(0) is viewport._canvas
    assert viewport._canvas_layout.stackingMode() == QStackedLayout.StackingMode.StackAll
    assert viewport._canvas_layout.indexOf(viewport.renderer) >= 0
    assert viewport._canvas_layout.indexOf(viewport._overlay_canvas) >= 0
    assert viewport._canvas_layout.currentWidget() is viewport._overlay_canvas
    assert viewport._overlay_canvas.isHidden()

    update = Mock()
    monkeypatch.setattr(viewport._overlay_canvas, "update", update)
    content["visible"] = True
    viewport.renderer.frameSwapped.emit()

    assert not viewport._overlay_canvas.isHidden()
    update.assert_called_once_with()
    assert app is not None


def test_public_overlay_imports_remain_graphics_free(tmp_path):
    environment = os.environ.copy()
    source_path = str(ROOT / "src")
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, [source_path, environment.get("PYTHONPATH")]))
    code = (
        "from compas_viewer import LegendOverlay, ScaleBarOverlay, ScreenTextOverlay; "
        "import sys; "
        "assert LegendOverlay and ScaleBarOverlay and ScreenTextOverlay; "
        "assert not any(name.startswith('PySide6') for name in sys.modules)"
    )

    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=tmp_path, env=environment)

    assert result.returncode == 0, result.stdout + result.stderr
