"""Transient screen-space overlays owned by COMPAS Viewer."""

from collections.abc import Iterable
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from math import floor
from math import isfinite
from math import log10
from math import radians
from math import tan
from numbers import Real
from typing import TYPE_CHECKING
from typing import Literal

from compas.colors import Color

if TYPE_CHECKING:
    from PySide6.QtGui import QPainter


@dataclass(frozen=True, slots=True)
class _OverlayContext:
    """Describe the viewport and camera values needed by screen overlays.

    Parameters
    ----------
    width
        Viewport width in logical pixels.
    height
        Viewport height in logical pixels.
    camera_distance
        Distance from the camera to its target in world units.
    field_of_view
        Vertical perspective field of view in degrees.
    perspective
        Whether the active projection is perspective.
    unit
        Optional informational unit appended to scale labels.
    precision
        Number of decimal places shown in scale labels.

    """

    width: int
    height: int
    camera_distance: float
    field_of_view: float
    perspective: bool
    unit: str | None = None
    precision: int = 3

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Overlay viewport dimensions must be positive.")
        if self.precision < 0:
            raise ValueError("Overlay precision cannot be negative.")


@dataclass(frozen=True, slots=True)
class _ScaleBarLayout:
    """Resolved scale-bar dimensions for one viewport frame.

    Parameters
    ----------
    world_length
        World distance represented by the bar.
    pixel_length
        Bar length in logical screen pixels.
    label
        Formatted scale label.
    depth_dependent
        Whether the scale is local to the camera-target depth.

    """

    world_length: float
    pixel_length: float
    label: str
    depth_dependent: bool


@dataclass(frozen=True, slots=True)
class ScaleBarOverlay:
    """Display world scale at the camera-target plane.

    The scale is global for orthographic projection. For perspective
    projection it is local to the camera-target depth and the rendered label
    states that limitation explicitly.

    Parameters
    ----------
    target_pixels
        Preferred screen length of the bar. The actual length is adjusted to
        a readable 1, 2, or 5 times a power of ten world distance.
    color
        Bar and label color.
    margin
        Distance from the lower-left viewport edges in logical pixels.

    """

    target_pixels: float = 120.0
    color: Color = field(default_factory=Color.black)
    margin: float = 20.0

    def __post_init__(self) -> None:
        if isinstance(self.target_pixels, bool) or not isinstance(self.target_pixels, Real):
            raise TypeError("Scale-bar target pixels must be a non-boolean number.")
        if not isfinite(self.target_pixels):
            raise ValueError("Scale-bar target pixels must be finite.")
        if self.target_pixels <= 0:
            raise ValueError("Scale-bar target pixels must be positive.")
        if isinstance(self.margin, bool) or not isinstance(self.margin, Real):
            raise TypeError("Scale-bar margin must be a non-boolean number.")
        if not isfinite(self.margin):
            raise ValueError("Scale-bar margin must be finite.")
        if self.margin < 0:
            raise ValueError("Scale-bar margin cannot be negative.")
        if not isinstance(self.color, Color):
            raise TypeError("Scale-bar color must be a COMPAS Color.")

    def _layout(self, context: _OverlayContext) -> _ScaleBarLayout:
        """Resolve a readable bar length for the current camera.

        Parameters
        ----------
        context
            Current viewport and camera values.

        Returns
        -------
        _ScaleBarLayout
            World length, screen length, and formatted label.

        Raises
        ------
        ValueError
            If the camera distance is not positive, or a perspective field of
            view is outside the open interval from zero to 180 degrees.

        """
        if context.camera_distance <= 0:
            raise ValueError("Scale-bar camera distance must be positive.")
        if context.perspective and not 0 < context.field_of_view < 180:
            raise ValueError("Scale-bar field of view must be between zero and 180 degrees.")

        if context.perspective:
            world_span = 2.0 * context.camera_distance * tan(radians(context.field_of_view) / 2.0)
            world_per_pixel = world_span / context.height
        else:
            world_per_pixel = 2.0 * context.camera_distance / context.width

        world_length = _nice_length(world_per_pixel * self.target_pixels)
        pixel_length = world_length / world_per_pixel
        label = f"{world_length:.{context.precision}f}"
        if context.unit:
            label = f"{label} {context.unit}"
        if context.perspective:
            label = f"{label} at target depth"
        return _ScaleBarLayout(
            world_length=world_length,
            pixel_length=pixel_length,
            label=label,
            depth_dependent=context.perspective,
        )


@dataclass(frozen=True, slots=True, init=False)
class LegendOverlay:
    """Display ordered categorical labels and colors.

    Parameters
    ----------
    entries
        Ordered `(label, color)` entries.
    title
        Optional legend title.

    """

    entries: tuple[tuple[str, Color], ...]
    title: str | None

    def __init__(self, entries: Iterable[tuple[str, Color]], title: str | None = None) -> None:
        resolved = tuple(entries)
        if not resolved:
            raise ValueError("A legend requires at least one entry.")
        for label, color in resolved:
            if not isinstance(label, str):
                raise TypeError("Legend labels must be strings.")
            if not isinstance(color, Color):
                raise TypeError("Legend colors must be COMPAS Color values.")
        if title is not None and not isinstance(title, str):
            raise TypeError("Legend title must be a string or None.")
        object.__setattr__(self, "entries", resolved)
        object.__setattr__(self, "title", title)


@dataclass(frozen=True, slots=True)
class ScreenTextOverlay:
    """Display text at a normalized viewport position.

    The position is independent of the camera. `(0, 0)` is the top-left of
    the viewport and `(1, 1)` is the bottom-right. Alignment determines which
    point of the rendered text bounds is placed at that position.

    Parameters
    ----------
    text
        Text to display.
    position
        Normalized viewport position.
    horizontal_alignment
        Horizontal alignment relative to the position.
    vertical_alignment
        Vertical alignment relative to the position.
    color
        Text color.

    """

    text: str
    position: tuple[float, float]
    horizontal_alignment: Literal["left", "center", "right"] = "left"
    vertical_alignment: Literal["top", "center", "bottom"] = "top"
    color: Color = field(default_factory=Color.white)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError("Screen-text content should be a string.")
        if not isinstance(self.position, tuple) or len(self.position) != 2:
            raise TypeError("Screen-text position should be a pair of normalized coordinates.")
        for coordinate in self.position:
            if isinstance(coordinate, bool) or not isinstance(coordinate, Real):
                raise TypeError("Screen-text position coordinates should be non-boolean numbers.")
            if not isfinite(coordinate):
                raise ValueError("Screen-text position coordinates should be finite.")
            if not 0 <= coordinate <= 1:
                raise ValueError("Screen-text position coordinates should be between zero and one.")
        if self.horizontal_alignment not in {"left", "center", "right"}:
            raise ValueError("Screen-text horizontal alignment should be left, center, or right.")
        if self.vertical_alignment not in {"top", "center", "bottom"}:
            raise ValueError("Screen-text vertical alignment should be top, center, or bottom.")
        if not isinstance(self.color, Color):
            raise TypeError("Screen-text color should be a COMPAS Color.")


type Overlay = ScaleBarOverlay | LegendOverlay | ScreenTextOverlay


class _OverlayLayer:
    """Store and draw the approved transient Viewer overlay types."""

    def __init__(self) -> None:
        self._items: list[Overlay] = []

    def __iter__(self) -> Iterator[Overlay]:
        """Iterate over overlays in drawing order."""
        return iter(self._items)

    def __len__(self) -> int:
        """Return the number of overlays in the layer."""
        return len(self._items)

    def add(self, overlay: Overlay) -> None:
        """Append an approved overlay to the drawing order.

        Parameters
        ----------
        overlay
            Scale bar, categorical legend, or screen text to add.

        Raises
        ------
        TypeError
            If the value is not an approved overlay type.
        ValueError
            If the same overlay instance is already present.

        """
        if not isinstance(overlay, (ScaleBarOverlay, LegendOverlay, ScreenTextOverlay)):
            raise TypeError("Viewer overlays must be ScaleBarOverlay, LegendOverlay, or ScreenTextOverlay values.")
        if any(item is overlay for item in self._items):
            raise ValueError("The overlay is already present in this Viewer.")
        self._items.append(overlay)

    def remove(self, overlay: Overlay) -> bool:
        """Remove an overlay by identity.

        Parameters
        ----------
        overlay
            Overlay instance to remove.

        Returns
        -------
        bool
            Whether the overlay was present.

        """
        for index, item in enumerate(self._items):
            if item is overlay:
                del self._items[index]
                return True
        return False

    def draw(self, painter: "QPainter", context: _OverlayContext) -> None:
        """Draw all overlays in their insertion order.

        Parameters
        ----------
        painter
            Active Qt painter for the Viewer viewport.
        context
            Current viewport and camera values.

        """
        from PySide6.QtCore import QRectF
        from PySide6.QtGui import QBrush
        from PySide6.QtGui import QColor
        from PySide6.QtGui import QPainter
        from PySide6.QtGui import QPen

        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setClipRect(QRectF(0.0, 0.0, float(context.width), float(context.height)))
        for overlay in self._items:
            if isinstance(overlay, ScaleBarOverlay):
                layout = overlay._layout(context)
                color = QColor.fromRgbF(*overlay.color.rgba)
                pen = QPen(color)
                pen.setWidthF(1.5)
                painter.setPen(pen)
                x = overlay.margin
                y = context.height - overlay.margin
                painter.drawLine(round(x), round(y), round(x + layout.pixel_length), round(y))
                painter.drawLine(round(x), round(y - 4), round(x), round(y + 4))
                painter.drawLine(round(x + layout.pixel_length), round(y - 4), round(x + layout.pixel_length), round(y + 4))
                painter.drawText(round(x), round(y - 8), layout.label)
                continue

            if isinstance(overlay, ScreenTextOverlay):
                metrics = painter.fontMetrics()
                bounds = metrics.boundingRect(overlay.text)
                anchor_x = overlay.position[0] * context.width
                anchor_y = overlay.position[1] * context.height

                if overlay.horizontal_alignment == "left":
                    left = anchor_x
                elif overlay.horizontal_alignment == "center":
                    left = anchor_x - bounds.width() / 2.0
                else:
                    left = anchor_x - bounds.width()

                if overlay.vertical_alignment == "top":
                    top = anchor_y
                elif overlay.vertical_alignment == "center":
                    top = anchor_y - bounds.height() / 2.0
                else:
                    top = anchor_y - bounds.height()

                color = QColor.fromRgbF(*overlay.color.rgba)
                painter.setPen(QPen(color))
                painter.drawText(round(left - bounds.left()), round(top - bounds.top()), overlay.text)
                continue

            metrics = painter.fontMetrics()
            padding = 8.0
            swatch = float(metrics.height())
            title_height = float(metrics.height()) if overlay.title else 0.0
            label_width = max(metrics.horizontalAdvance(label) for label, _ in overlay.entries)
            box_width = padding * 3 + swatch + label_width
            box_height = padding * 2 + title_height + len(overlay.entries) * swatch
            x = context.width - 20.0 - box_width
            y = 20.0
            background = QColor(255, 255, 255, 220)
            painter.setPen(QPen(QColor(0, 0, 0, 180)))
            painter.setBrush(QBrush(background))
            painter.drawRoundedRect(QRectF(x, y, box_width, box_height), 3.0, 3.0)
            cursor = y + padding + metrics.ascent()
            if overlay.title:
                painter.setPen(QPen(QColor(0, 0, 0)))
                painter.drawText(round(x + padding), round(cursor), overlay.title)
                cursor += title_height
            for label, color in overlay.entries:
                row_top = cursor - metrics.ascent()
                qcolor = QColor.fromRgbF(*color.rgba)
                painter.setPen(QPen(qcolor))
                painter.setBrush(QBrush(qcolor))
                painter.drawRect(QRectF(x + padding, row_top, swatch, swatch))
                painter.setPen(QPen(QColor(0, 0, 0)))
                painter.drawText(round(x + padding * 2 + swatch), round(cursor), label)
                cursor += swatch


def _nice_length(value: float) -> float:
    """Return the nearest 1, 2, or 5 times a power of ten value."""
    if value <= 0:
        raise ValueError("Scale length must be positive.")
    exponent = floor(log10(value))
    base = 10.0**exponent
    normalized = value / base
    factor = min((1.0, 2.0, 5.0, 10.0), key=lambda candidate: abs(log10(candidate / normalized)))
    return factor * base


__all__ = ["LegendOverlay", "Overlay", "ScaleBarOverlay", "ScreenTextOverlay"]
