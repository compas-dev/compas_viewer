"""Transient Viewer-owned distance measurement state."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Literal

from compas.geometry import Point
from compas.geometry import distance_point_point
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas_viewer.snapping import SnapQuery
from compas_viewer.snapping import SnapResult

if TYPE_CHECKING:
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QColor
    from PySide6.QtGui import QPainter

    from compas_viewer.snapping import ProjectedPoint

__all__ = [
    "DistanceInspection",
    "MeasurementMode",
    "MeasurementState",
    "PersistentMeasurementMode",
    "SNAP_RADIUS",
]


type MeasurementMode = Literal["inactive", "inspection", "fixed", "associative"]
type PersistentMeasurementMode = Literal["fixed", "associative"]

SNAP_RADIUS = 18.0


@dataclass(frozen=True, slots=True)
class DistanceInspection:
    """A completed transient distance inspection.

    Parameters
    ----------
    start
        First inspected world-coordinate point.
    end
        Second inspected world-coordinate point.

    """

    start: Point
    end: Point

    @property
    def distance(self) -> float:
        """float: Distance between the two inspected points."""
        return distance_point_point(self.start, self.end)


class MeasurementState:
    """Store one transient, one-shot distance measurement interaction.

    Parameters
    ----------
    changed
        Callback invoked after each effective state change.

    Notes
    -----
    The state belongs to the live Viewer. It is not serialized with the scene
    or Viewer configuration.

    """

    def __init__(self, changed: Callable[[], None] | None = None) -> None:
        self._changed = changed
        self.mode: MeasurementMode = "inactive"
        self.first_snap: SnapResult | None = None
        self.hover_snap: SnapResult | None = None
        self.available_points: tuple[SnapResult, ...] = ()
        self.completed_inspection: DistanceInspection | None = None
        self.rejection: str | None = None

    @property
    def active(self) -> bool:
        """bool: Whether a measurement is acquiring anchors."""
        return self.mode != "inactive"

    @property
    def has_transient_state(self) -> bool:
        """bool: Whether active or retained measurement state exists."""
        return self.active or self.completed_inspection is not None

    def start(self, mode: Literal["inspection", "fixed", "associative"]) -> None:
        """Start a one-shot distance interaction and clear earlier results.

        Parameters
        ----------
        mode
            Transient inspection, fixed dimension, or associative dimension.

        Raises
        ------
        ValueError
            If `mode` is unsupported.

        """
        if mode not in {"inspection", "fixed", "associative"}:
            raise ValueError(f"Unsupported distance measurement mode: {mode!r}.")
        self.mode = mode
        self.first_snap = None
        self.hover_snap = None
        self.available_points = ()
        self.completed_inspection = None
        self.rejection = None
        self._notify()

    def cancel(self) -> bool:
        """Clear active and retained measurement state.

        Returns
        -------
        bool
            Whether any transient state was cleared.

        """
        if not self.has_transient_state and self.first_snap is None and self.hover_snap is None and self.rejection is None:
            return False
        self.mode = "inactive"
        self.first_snap = None
        self.hover_snap = None
        self.available_points = ()
        self.completed_inspection = None
        self.rejection = None
        self._notify()
        return True

    def update_hover(self, query: SnapQuery) -> None:
        """Update hover guidance without changing the first anchor.

        Parameters
        ----------
        query
            Current accepted winner and all projected discrete point snaps of
            the hovered object. An empty query represents the background.

        """
        if not self.active:
            return
        if self._set_hover(query):
            self._notify()

    def accept(
        self,
        query: SnapQuery,
        *,
        unit: str | None,
        precision: int,
    ) -> DistanceInspection | DistanceDimension | None:
        """Accept one snapped anchor and complete after the second.

        Parameters
        ----------
        query
            Current depth-qualified winner and projected point palette. An
            empty query represents the background.
        unit
            Informational unit snapshot for a persistent dimension.
        precision
            Display-precision snapshot for a persistent dimension.

        Returns
        -------
        DistanceInspection | DistanceDimension | None
            A completed transient inspection or persistent dimension. The
            first accepted anchor and rejected clicks return `None`.

        """
        if not self.active:
            return None
        snap = query.winner
        if snap is None:
            if self._set_hover(query):
                self._notify()
            return None
        if self.mode == "associative" and not snap.supports_association:
            if self._set_hover(query):
                self._notify()
            return None

        self.hover_snap = snap
        self.available_points = query.points
        self.rejection = None
        if self.first_snap is None:
            self.first_snap = snap
            self._notify()
            return None

        first = self.first_snap
        mode = self.mode
        if mode == "inspection":
            result: DistanceInspection | DistanceDimension = DistanceInspection(
                _copy_point(first.point),
                _copy_point(snap.point),
            )
            self.completed_inspection = result
        elif mode == "fixed":
            result = DistanceDimension(
                PointAnchor(first.point),
                PointAnchor(snap.point),
                unit=unit,
                precision=precision,
            )
        else:
            first_anchor = first.component_anchor()
            second_anchor = snap.component_anchor()
            if first_anchor is None or second_anchor is None:
                raise RuntimeError("Associative measurement accepted an unsupported snap.")
            result = DistanceDimension(first_anchor, second_anchor, unit=unit, precision=precision)

        self.mode = "inactive"
        self.first_snap = None
        self.hover_snap = None
        self.available_points = ()
        self.rejection = None
        self._notify()
        return result

    def _set_hover(self, query: SnapQuery) -> bool:
        """Apply one hover query and report whether transient state changed."""
        snap = query.winner
        rejection = None
        if self.mode == "associative" and snap is not None and not snap.supports_association:
            rejection = snap.association_error
        if self.hover_snap == snap and self.available_points == query.points and self.rejection == rejection:
            return False
        self.hover_snap = snap
        self.available_points = query.points
        self.rejection = rejection
        return True

    def _notify(self) -> None:
        if self._changed is not None:
            self._changed()


def _copy_point(point: Point) -> Point:
    return Point(point.x, point.y, point.z)


def _draw_measurement_preview(
    painter: "QPainter",
    state: MeasurementState,
    project: Callable[[Point], "ProjectedPoint | None"],
    *,
    unit: str | None,
    precision: int,
) -> None:
    """Draw active or retained transient measurement state.

    Parameters
    ----------
    painter
        Active painter for the Viewer viewport.
    state
        Viewer-owned measurement interaction state.
    project
        Current world-to-screen projection supplied by the renderer.
    unit
        Informational unit appended to live distance labels.
    precision
        Number of decimal places shown in live distance labels.

    Notes
    -----
    Stored points remain in world coordinates and are projected for every
    frame. Camera navigation therefore updates the preview without mutating
    measurement state.

    """
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QColor
    from PySide6.QtGui import QPainter
    from PySide6.QtGui import QPen

    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    preview_color = QColor(255, 140, 0)
    available_color = QColor(90, 210, 255, 235)
    rejection_color = QColor(210, 45, 45)

    inspection = state.completed_inspection
    if inspection is not None:
        _draw_measurement_segment(
            painter,
            inspection.start,
            inspection.end,
            project,
            preview_color,
            _format_distance(inspection.distance, unit, precision),
        )
        return

    for snap in state.available_points:
        projected = project(snap.point)
        if projected is not None:
            _draw_available_snap_marker(painter, QPointF(projected.x, projected.y), available_color)

    first = state.first_snap
    hover = state.hover_snap
    if state.rejection and hover is not None:
        if first is not None:
            first_projection = project(first.point)
            if first_projection is not None:
                _draw_measurement_marker(painter, QPointF(first_projection.x, first_projection.y), preview_color)
        hover_projection = project(hover.point)
        if hover_projection is not None:
            point = QPointF(hover_projection.x, hover_projection.y)
            _draw_measurement_marker(painter, point, rejection_color)
            painter.setPen(QPen(rejection_color))
            painter.drawText(point + QPointF(8.0, -8.0), state.rejection)
        return

    if first is not None and hover is not None:
        _draw_measurement_segment(
            painter,
            first.point,
            hover.point,
            project,
            preview_color,
            _format_distance(distance_point_point(first.point, hover.point), unit, precision),
        )
    else:
        snap = first or hover
        if snap is not None:
            projected = project(snap.point)
            if projected is not None:
                _draw_measurement_marker(painter, QPointF(projected.x, projected.y), preview_color)


def _draw_measurement_segment(
    painter: "QPainter",
    start: Point,
    end: Point,
    project: Callable[[Point], "ProjectedPoint | None"],
    color: "QColor",
    label: str,
) -> None:
    """Draw projected endpoints, segment, and label when visible."""
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QPen

    start_projection = project(start)
    end_projection = project(end)
    if start_projection is None and end_projection is None:
        return

    start_point = QPointF(start_projection.x, start_projection.y) if start_projection is not None else None
    end_point = QPointF(end_projection.x, end_projection.y) if end_projection is not None else None
    if start_point is not None:
        _draw_measurement_marker(painter, start_point, color)
    if end_point is not None:
        _draw_measurement_marker(painter, end_point, color)
    if start_point is None or end_point is None:
        return

    painter.setPen(QPen(color, 2.0))
    painter.drawLine(start_point, end_point)
    midpoint = QPointF(0.5 * (start_point.x() + end_point.x()), 0.5 * (start_point.y() + end_point.y()))
    painter.drawText(midpoint + QPointF(8.0, -8.0), label)


def _draw_measurement_marker(painter: "QPainter", point: "QPointF", color: "QColor") -> None:
    """Draw one filled square screen marker."""
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QBrush
    from PySide6.QtGui import QPen

    painter.setPen(QPen(color, 2.0))
    painter.setBrush(QBrush(color))
    painter.drawRect(QRectF(point.x() - 5.0, point.y() - 5.0, 10.0, 10.0))


def _draw_available_snap_marker(painter: "QPainter", point: "QPointF", color: "QColor") -> None:
    """Draw one bright hollow square point-snap guide."""
    from PySide6.QtCore import QRectF
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QBrush
    from PySide6.QtGui import QPen

    painter.setPen(QPen(color, 2.0))
    painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
    painter.drawRect(QRectF(point.x() - 5.0, point.y() - 5.0, 10.0, 10.0))


def _format_distance(distance: float, unit: str | None, precision: int) -> str:
    """Return a live distance label using current Viewer settings."""
    label = f"{distance:.{precision}f}"
    return f"{label} {unit}" if unit else label
