from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from PySide6.QtCore import QPointF

from compas.geometry import Point
from compas_viewer import Viewer
from compas_viewer.measurement import MeasurementState
from compas_viewer.measurement import _draw_measurement_preview
from compas_viewer.overlays import _OverlayLayer
from compas_viewer.snapping import ProjectedPoint
from compas_viewer.snapping import SnapKind
from compas_viewer.snapping import SnapResult
import compas_viewer.viewer as viewer_module


def snap(xyz, *, association_error=None):
    return SnapResult(
        Point(*xyz),
        uuid4(),
        SnapKind.FACE if association_error else SnapKind.POINT,
        0.0,
        association_error=association_error,
    )


def project(point):
    return ProjectedPoint(point.x * 10.0, point.y * 10.0, 0.5)


def drawn_text(painter):
    return [call.args[1] for call in painter.drawText.call_args_list]


def test_active_preview_reprojects_markers_and_formats_live_distance():
    state = MeasurementState()
    state.start("fixed")
    state.accept(snap([0, 0, 0]), unit=None, precision=3)
    state.update_hover(snap([3, 4, 0]))
    painter = Mock()
    projection = Mock(side_effect=project)

    _draw_measurement_preview(painter, state, projection, unit="m", precision=2)

    assert projection.call_count == 2
    painter.drawLine.assert_called_once_with(QPointF(0, 0), QPointF(30, 40))
    assert drawn_text(painter) == ["5.00 m"]
    assert painter.drawEllipse.call_count == 2


def test_completed_inspection_uses_current_unit_and_precision_each_frame():
    state = MeasurementState()
    state.start("inspection")
    state.accept(snap([0, 0, 0]), unit="stored", precision=0)
    state.accept(snap([3, 4, 0]), unit="stored", precision=0)
    painter = Mock()

    _draw_measurement_preview(painter, state, project, unit="cm", precision=1)
    _draw_measurement_preview(painter, state, project, unit=None, precision=3)

    assert drawn_text(painter) == ["5.0 cm", "5.000"]


def test_preview_skips_hidden_segment_endpoints_but_keeps_visible_marker():
    state = MeasurementState()
    state.start("fixed")
    state.accept(snap([0, 0, 0]), unit=None, precision=3)
    state.update_hover(snap([1, 0, 0]))
    painter = Mock()

    def partially_visible(point):
        if point.x == 0:
            return None
        return ProjectedPoint(10, 20, 0.5)

    _draw_measurement_preview(painter, state, partially_visible, unit=None, precision=3)

    painter.drawEllipse.assert_called_once()
    painter.drawLine.assert_not_called()
    painter.drawText.assert_not_called()


def test_associative_rejection_is_drawn_at_the_projected_hover_snap():
    state = MeasurementState()
    state.start("associative")
    state.update_hover(snap([1, 2, 0], association_error="Face snaps are fixed only"))
    painter = Mock()

    _draw_measurement_preview(painter, state, project, unit=None, precision=3)

    assert drawn_text(painter) == ["Face snaps are fixed only"]
    assert painter.drawEllipse.call_count == 1
    painter.drawLine.assert_not_called()


def test_rejected_second_associative_anchor_does_not_preview_a_dimension():
    state = MeasurementState()
    state.start("associative")
    state.accept(snap([0, 0, 0]), unit=None, precision=3)
    state.update_hover(snap([3, 4, 0], association_error="Face snaps are fixed only"))
    painter = Mock()

    _draw_measurement_preview(painter, state, project, unit="m", precision=2)

    assert painter.drawEllipse.call_count == 2
    painter.drawLine.assert_not_called()
    assert drawn_text(painter) == ["Face snaps are fixed only"]


def test_measurement_preview_draws_with_qpainter():
    from PySide6.QtGui import QColor
    from PySide6.QtGui import QImage
    from PySide6.QtGui import QPainter
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    image = QImage(80, 60, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor(0, 0, 0, 0))
    painter = QPainter(image)
    state = MeasurementState()
    state.start("inspection")
    state.accept(snap([1, 2, 0]), unit=None, precision=3)
    state.update_hover(snap([5, 2, 0]))

    _draw_measurement_preview(painter, state, project, unit="m", precision=2)
    painter.end()

    assert app is not None
    assert image.pixelColor(30, 20).alpha() > 0


def test_viewer_draws_measurement_after_regular_overlays(monkeypatch):
    order = []

    class Layer:
        def __bool__(self):
            return True

        def draw(self, painter, context):
            order.append("overlay")

    measurement = MeasurementState()
    measurement.start("fixed")
    viewer = SimpleNamespace(
        _overlay_layer=Layer(),
        state=SimpleNamespace(measurement=measurement),
        config=SimpleNamespace(measurement=SimpleNamespace(unit="m", precision=2)),
    )
    renderer = SimpleNamespace(
        width=lambda: 640,
        height=lambda: 480,
        camera=SimpleNamespace(distance=10, fov=45),
        view="perspective",
        project_point=project,
    )
    painter = Mock()
    monkeypatch.setattr(viewer_module, "QPainter", Mock(return_value=painter))
    monkeypatch.setattr(viewer_module, "_draw_measurement_preview", lambda *args, **kwargs: order.append("measurement"))

    Viewer._draw_overlays(viewer, renderer)

    assert order == ["overlay", "measurement"]
    painter.end.assert_called_once_with()


def test_viewer_creates_painter_for_measurement_without_regular_overlays(monkeypatch):
    measurement = MeasurementState()
    measurement.start("inspection")
    viewer = SimpleNamespace(
        _overlay_layer=_OverlayLayer(),
        state=SimpleNamespace(measurement=measurement),
        config=SimpleNamespace(measurement=SimpleNamespace(unit=None, precision=3)),
    )
    renderer = SimpleNamespace(width=lambda: 640, height=lambda: 480, project_point=project)
    painter = Mock()
    painter_type = Mock(return_value=painter)
    preview = Mock()
    monkeypatch.setattr(viewer_module, "QPainter", painter_type)
    monkeypatch.setattr(viewer_module, "_draw_measurement_preview", preview)

    Viewer._draw_overlays(viewer, renderer)

    painter_type.assert_called_once_with(renderer)
    preview.assert_called_once()
    painter.end.assert_called_once_with()


def test_viewer_skips_painter_without_overlays_or_measurement(monkeypatch):
    viewer = SimpleNamespace(
        _overlay_layer=_OverlayLayer(),
        state=SimpleNamespace(measurement=MeasurementState()),
    )
    renderer = SimpleNamespace(width=lambda: 640, height=lambda: 480)
    painter_type = Mock()
    monkeypatch.setattr(viewer_module, "QPainter", painter_type)

    Viewer._draw_overlays(viewer, renderer)

    painter_type.assert_not_called()
