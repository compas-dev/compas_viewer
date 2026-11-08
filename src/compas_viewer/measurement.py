"""Transient Viewer-owned distance measurement state."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from compas.geometry import Point
from compas.geometry import distance_point_point
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas_viewer.snapping import SnapResult

__all__ = [
    "DistanceInspection",
    "MeasurementMode",
    "MeasurementState",
    "PersistentMeasurementMode",
    "SNAP_RADIUS",
]


type MeasurementMode = Literal["inactive", "inspection", "fixed", "associative"]
type PersistentMeasurementMode = Literal["fixed", "associative"]

SNAP_RADIUS = 12.0


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
        self.completed_inspection = None
        self.rejection = None
        self._notify()
        return True

    def update_hover(self, snap: SnapResult | None) -> None:
        """Update the current hover snap without changing the first anchor.

        Parameters
        ----------
        snap
            Current semantic snap, or `None` over the background.

        """
        if not self.active:
            return
        rejection = None
        if self.mode == "associative" and snap is not None and not snap.supports_association:
            rejection = snap.association_error
        if self.hover_snap is snap and self.rejection == rejection:
            return
        self.hover_snap = snap
        self.rejection = rejection
        self._notify()

    def accept(
        self,
        snap: SnapResult | None,
        *,
        unit: str | None,
        precision: int,
    ) -> DistanceInspection | DistanceDimension | None:
        """Accept one snapped anchor and complete after the second.

        Parameters
        ----------
        snap
            Semantic snap under the pointer, or `None` over the background.
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
        if snap is None:
            self.update_hover(None)
            return None
        if self.mode == "associative" and not snap.supports_association:
            self.update_hover(snap)
            return None

        self.hover_snap = snap
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
        self.rejection = None
        self._notify()
        return result

    def _notify(self) -> None:
        if self._changed is not None:
            self._changed()


def _copy_point(point: Point) -> Point:
    return Point(point.x, point.y, point.z)
