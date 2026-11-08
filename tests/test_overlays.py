from importlib import import_module
from math import isclose
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from typing import cast

import pytest

from compas.colors import Color
from compas_viewer import LegendOverlay
from compas_viewer import ScaleBarOverlay
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

    layer.add(scale)
    layer.add(legend)

    assert tuple(layer) == (scale, legend)
    assert layer.remove(scale)
    assert tuple(layer) == (legend,)
    assert not layer.remove(scale)


def test_overlay_layer_rejects_duplicates_and_unapproved_types():
    layer = _OverlayLayer()
    scale = ScaleBarOverlay()
    layer.add(scale)

    with pytest.raises(ValueError, match="already present"):
        layer.add(scale)
    with pytest.raises(TypeError, match="ScaleBarOverlay or LegendOverlay"):
        layer.add(cast(Overlay, object()))


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


def test_viewer_overlay_facade_does_not_change_scene_serialization():
    viewer = object.__new__(Viewer)
    viewer._overlay_layer = _OverlayLayer()
    viewer._scene = ViewerScene()
    viewer.running = False
    before = viewer.scene.__data__
    scale = ScaleBarOverlay()

    viewer.add_overlay(scale)

    assert viewer.overlays == (scale,)
    assert viewer.scene.__data__ == before
    assert viewer.scene.objects == []
    assert viewer.remove_overlay(scale)
    assert viewer.overlays == ()


def test_renderer_draws_overlays_only_for_display_rendering(monkeypatch):
    renderer_module = import_module("compas_viewer.renderer.renderer")
    overlay_draws = []
    paint_modes = []
    fake = SimpleNamespace(
        viewer=SimpleNamespace(_draw_overlays=lambda renderer: overlay_draws.append(renderer)),
        rendermode="shaded",
        _frames=0,
        _now=float("inf"),
        clear=lambda: None,
        width=lambda: 640,
        height=lambda: 480,
        devicePixelRatio=lambda: 2,
        paint=lambda is_instance=False: paint_modes.append(is_instance),
    )
    monkeypatch.setattr(renderer_module.GL, "glViewport", lambda *_args: None)

    Renderer.paintGL(fake)
    Renderer.paintGL(fake, is_instance=True)

    assert paint_modes == [False, True]
    assert overlay_draws == [fake]


def test_public_overlay_imports_remain_graphics_free(tmp_path):
    environment = os.environ.copy()
    source_path = str(ROOT / "src")
    environment["PYTHONPATH"] = os.pathsep.join(filter(None, [source_path, environment.get("PYTHONPATH")]))
    code = (
        "from compas_viewer import LegendOverlay, ScaleBarOverlay; "
        "import sys; "
        "assert LegendOverlay and ScaleBarOverlay; "
        "assert not any(name.startswith('PySide6') for name in sys.modules)"
    )

    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=tmp_path, env=environment)

    assert result.returncode == 0, result.stdout + result.stderr
