from typing import Any
from typing import Self
from typing import cast

from OpenGL import GL

from compas.colors import Color
from compas.geometry import Geometry
from compas.geometry import Point
from compas.geometry import Transformation
from compas.scene import GeometryObject
from compas_viewer.gl import make_index_buffer
from compas_viewer.gl import make_vertex_buffer

from .sceneobject import ViewerSceneObject


class ArrowOverlay(Geometry):
    """Screen-scaled arrow connecting two points in 3D space.

    Parameters
    ----------
    start
        Arrow start point in world coordinates.
    end
        Arrow tip point in world coordinates.
    color
        Arrow color.
    linewidth
        Shaft width in screen pixels.
    head_length
        Arrowhead length in screen pixels.
    head_width
        Arrowhead width in screen pixels.
    opacity
        Arrow opacity between zero and one.
    on_top
        Whether to draw over scene geometry instead of using depth testing.

    """

    def __init__(
        self,
        start: Point | tuple[float, float, float],
        end: Point | tuple[float, float, float],
        color: Color | None = None,
        linewidth: float = 3,
        head_length: float = 16,
        head_width: float = 12,
        opacity: float = 1,
        on_top: bool = True,
    ) -> None:
        super().__init__()
        if linewidth <= 0:
            raise ValueError("Arrow line width must be positive.")
        if head_length <= 0 or head_width <= 0:
            raise ValueError("Arrowhead dimensions must be positive.")
        if not 0 <= opacity <= 1:
            raise ValueError("Arrow opacity must be between zero and one.")

        start_point = Point(start[0], start[1], start[2])
        end_point = Point(end[0], end[1], end[2])
        if start_point == end_point:
            raise ValueError("Arrow start and end points must be different.")

        self.start = start_point
        self.end = end_point
        self.color = color or Color.black()
        self.linewidth = float(linewidth)
        self.head_length = float(head_length)
        self.head_width = float(head_width)
        self.opacity = float(opacity)
        self.on_top = on_top

    @property
    def __data__(self) -> dict[str, Any]:
        """dict[str, Any]: Serializable arrow-overlay data."""
        return {
            "start": self.start,
            "end": self.end,
            "color": self.color,
            "linewidth": self.linewidth,
            "head_length": self.head_length,
            "head_width": self.head_width,
            "opacity": self.opacity,
            "on_top": self.on_top,
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Self:
        """Construct an arrow overlay from serialized data."""
        return cls(**data)

    def transform(self, transformation: Transformation) -> None:
        """Transform both arrow anchors.

        Parameters
        ----------
        transformation
            Transformation applied to the start and end points.

        """
        self.start.transform(transformation)
        self.end.transform(transformation)


class ArrowOverlayObject(ViewerSceneObject, GeometryObject):
    """Render an arrow as a constant-pixel-size overlay."""

    @property
    def arrow(self) -> ArrowOverlay:
        """ArrowOverlay: The typed overlay geometry."""
        return cast(ArrowOverlay, self.geometry)

    def init(self) -> None:
        """Create the arrow mesh and update its bounds."""
        # Vertex fields are stage, signed side, and width kind. Stage 0 is the
        # start, 1 is the arrowhead base, and 2 is the tip. Width kind 0 uses
        # shaft width; 1 uses arrowhead width.
        vertices = [
            0,
            -0.5,
            0,
            1,
            -0.5,
            0,
            0,
            0.5,
            0,
            0,
            0.5,
            0,
            1,
            -0.5,
            0,
            1,
            0.5,
            0,
            1,
            -0.5,
            1,
            2,
            0,
            1,
            1,
            0.5,
            1,
        ]
        self._arrow_buffer = {
            "positions": make_vertex_buffer(vertices),
            "elements": make_index_buffer(range(9)),
            "n": 9,
        }
        self._update_bounding_box([self.arrow.start, self.arrow.end])
        self._inited = True

    def update(self, update_transform: bool = True, update_data: bool = False) -> None:
        """Update the overlay after changing its anchors or style.

        Parameters
        ----------
        update_transform
            Whether to redraw after a transformation change.
        update_data
            Whether to recalculate the arrow bounds.

        """
        if update_data:
            self._update_bounding_box([self.arrow.start, self.arrow.end])
        if update_transform or update_data:
            self.viewer.renderer.update()

    def draw_overlay(self, shader: Any, width: int, height: int) -> None:
        """Draw the arrow overlay.

        Parameters
        ----------
        shader
            Shader configured for arrow-overlay rendering.
        width
            Viewport width in pixels.
        height
            Viewport height in pixels.

        """
        if not self.show:
            return
        if self.arrow.on_top:
            GL.glDisable(GL.GL_DEPTH_TEST)
        try:
            shader.enable_attribute("position")
            if self.worldtransformation is not None:
                shader.uniform4x4("transform", self.worldtransformation.matrix)
            shader.uniform2f("screen_size", (width, height))
            shader.uniform3f("start_position", self.arrow.start)
            shader.uniform3f("end_position", self.arrow.end)
            shader.uniform3f("arrow_color", self.arrow.color.rgb)
            shader.uniform1f("arrow_opacity", self.arrow.opacity * self.opacity)
            shader.uniform1f("line_width", self.arrow.linewidth)
            shader.uniform1f("head_length", self.arrow.head_length)
            shader.uniform1f("head_width", self.arrow.head_width)
            shader.uniform1f("is_selected", self.is_selected)
            shader.bind_attribute("position", self._arrow_buffer["positions"])
            shader.draw_triangles(elements=self._arrow_buffer["elements"], n=self._arrow_buffer["n"])
            shader.disable_attribute("position")
        finally:
            if self.arrow.on_top:
                GL.glEnable(GL.GL_DEPTH_TEST)

    def _read_points_data(self) -> None:
        return None

    def _read_lines_data(self) -> None:
        return None

    def _read_frontfaces_data(self) -> None:
        return None

    def _read_backfaces_data(self) -> None:
        return None


__all__ = ["ArrowOverlay", "ArrowOverlayObject"]
