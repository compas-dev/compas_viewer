"""Transient render helpers for backend-neutral scene annotations."""

from math import ceil
from typing import Any
from typing import cast

from freetype import FT_LOAD_FLAGS
from freetype import Face
from numpy import array
from numpy import float32
from numpy import identity
from numpy import maximum
from numpy import zeros
from OpenGL import GL

from compas.geometry import Point
from compas.scene import ArrowAnnotation
from compas.scene import DistanceDimension
from compas.scene import TextAnnotation
from compas_viewer import HERE
from compas_viewer.gl import make_index_buffer
from compas_viewer.gl import make_vertex_buffer

from .sceneobject import ViewerSceneObject

FONT = HERE / "assets" / "fonts" / "FreeSans.ttf"
RASTER_HEIGHT = 48
UNRESOLVED_LABEL = "Unresolved"


class WorldAnnotationRenderObject(ViewerSceneObject):
    """Base class for render-only world annotations.

    World annotations own their OpenGL resources and do not contribute geometry
    to the shared scene buffers or instance-selection pass.

    """

    def refresh_annotation_bounds(self) -> None:
        """Recompute the annotation's current world-space bounds."""
        raise NotImplementedError

    def draw_world_annotation(self, renderer: Any, viewworld: Any) -> None:
        """Draw the annotation in the display pass.

        Parameters
        ----------
        renderer
            Active Viewer renderer.
        viewworld
            Current world-to-view transformation matrix.

        """
        raise NotImplementedError

    def _read_points_data(self) -> None:
        return None

    def _read_lines_data(self) -> None:
        return None

    def _read_frontfaces_data(self) -> None:
        return None

    def _read_backfaces_data(self) -> None:
        return None


class TextAnnotationRenderObject(WorldAnnotationRenderObject):
    """Render a core text annotation as a camera-facing billboard."""

    VERTICAL_ALIGN = {"top": 1, "center": 0, "bottom": -1}
    HORIZONTAL_ALIGN = {"left": -1, "center": 0, "right": 1}

    @property
    def annotation(self) -> TextAnnotation:
        """Return the represented text annotation."""
        return cast(TextAnnotation, self.item)

    def init(self) -> None:
        """Create the text texture and quad buffers."""
        self._text_buffer, self.text_aspect, self.rendered_height = _make_text_buffer(
            self.annotation.text,
            self.annotation.height,
        )
        self.refresh_annotation_bounds()
        self._inited = True

    def update(self, update_transform: bool = True, update_data: bool = False) -> None:
        """Update annotation resources after a data or transform change."""
        if update_data:
            self.clear()
            self.init()
        if update_transform or update_data:
            self.viewer.renderer.update()

    def clear(self) -> None:
        """Release the annotation's OpenGL resources."""
        buffer = getattr(self, "_text_buffer", None)
        if buffer is not None:
            _delete_text_buffer(buffer)
            del self._text_buffer
        self._inited = False

    def draw_world_annotation(self, renderer: Any, viewworld: Any) -> None:
        """Draw the text annotation in the display pass."""
        if not self.show:
            return
        shader = renderer.shader_world_text
        shader.bind()
        shader.uniform4x4("viewworld", viewworld)
        _draw_text(
            shader,
            self._text_buffer,
            position=self.annotation.anchor,
            transform=self.worldtransformation.matrix,
            color=self.color.rgb,
            opacity=self.opacity,
            screen_space=self.annotation.height_mode == "screen",
            screen_size=(renderer.width(), renderer.height()),
            text_aspect=self.text_aspect,
            text_height=self.rendered_height,
            vertical_align=self.VERTICAL_ALIGN[self.annotation.vertical_alignment],
            horizontal_align=self.HORIZONTAL_ALIGN[self.annotation.horizontal_alignment],
            is_selected=self.is_selected,
        )
        shader.release()

    def refresh_annotation_bounds(self) -> None:
        """Recompute the transformed text-anchor bounds."""
        self._update_bounding_box([self.annotation.anchor])


class ArrowAnnotationRenderObject(WorldAnnotationRenderObject):
    """Render a core arrow annotation with a constant-pixel-width shaft."""

    @property
    def annotation(self) -> ArrowAnnotation:
        """Return the represented arrow annotation."""
        return cast(ArrowAnnotation, self.item)

    def init(self) -> None:
        """Create the arrow buffers and update local bounds."""
        self._arrow_buffer = _make_arrow_buffer()
        self.refresh_annotation_bounds()
        self._inited = True

    def update(self, update_transform: bool = True, update_data: bool = False) -> None:
        """Update annotation bounds after a data or transform change."""
        if update_data:
            self.refresh_annotation_bounds()
        if update_transform or update_data:
            self.viewer.renderer.update()

    def clear(self) -> None:
        """Release the annotation's OpenGL resources."""
        buffer = getattr(self, "_arrow_buffer", None)
        if buffer is not None:
            _delete_arrow_buffer(buffer)
            del self._arrow_buffer
        self._inited = False

    def draw_world_annotation(self, renderer: Any, viewworld: Any) -> None:
        """Draw the arrow annotation in the display pass."""
        if not self.show:
            return
        shader = renderer.shader_world_arrow
        shader.bind()
        shader.uniform4x4("viewworld", viewworld)
        _draw_arrow(
            shader,
            self._arrow_buffer,
            start=self.annotation.start,
            end=self.annotation.end,
            transform=self.worldtransformation.matrix,
            color=self.color.rgb,
            opacity=self.opacity,
            screen_size=(renderer.width(), renderer.height()),
            is_selected=self.is_selected,
        )
        shader.release()

    def refresh_annotation_bounds(self) -> None:
        """Recompute the transformed arrow bounds."""
        self._update_bounding_box([self.annotation.start, self.annotation.end])


class DistanceDimensionRenderObject(WorldAnnotationRenderObject):
    """Render a resolved distance and its formatted label."""

    @property
    def dimension(self) -> DistanceDimension:
        """Return the represented distance dimension."""
        return cast(DistanceDimension, self.item)

    def init(self) -> None:
        """Create arrow and label resources for the dimension."""
        self._arrow_buffer = _make_arrow_buffer()
        self._label = self.display_label
        self._text_buffer, self.text_aspect, self.rendered_height = _make_text_buffer(self._label, 12.0)
        self.refresh_annotation_bounds()
        self._inited = True

    @property
    def resolved_points(self) -> tuple[Point, Point] | None:
        """Return the dimension's current world-coordinate endpoints."""
        return self.dimension.resolve(self.runtime_scene, self.worldtransformation)

    @property
    def display_label(self) -> str:
        """Return the resolved label or an explicit unresolved-state label."""
        label = self.dimension.formatted_label(self.runtime_scene, self.worldtransformation)
        if self.resolved_points is not None:
            return cast(str, label)
        if label:
            return f"{label} ({UNRESOLVED_LABEL.lower()})"
        return UNRESOLVED_LABEL

    @property
    def label_position(self) -> Point:
        """Return the world-coordinate position of the current label."""
        points = self.resolved_points
        if points is not None:
            return Point(
                0.5 * (points[0].x + points[1].x),
                0.5 * (points[0].y + points[1].y),
                0.5 * (points[0].z + points[1].z),
            )
        point = Point(0, 0, 0)
        point.transform(self.worldtransformation)
        return point

    def update(self, update_transform: bool = True, update_data: bool = False) -> None:
        """Refresh dynamic dimension state and request a redraw."""
        if update_transform or update_data:
            self._refresh_label()
            self.refresh_annotation_bounds()
            self.viewer.renderer.update()

    def clear(self) -> None:
        """Release the dimension's OpenGL resources."""
        text_buffer = getattr(self, "_text_buffer", None)
        if text_buffer is not None:
            _delete_text_buffer(text_buffer)
            del self._text_buffer
        arrow_buffer = getattr(self, "_arrow_buffer", None)
        if arrow_buffer is not None:
            _delete_arrow_buffer(arrow_buffer)
            del self._arrow_buffer
        self._inited = False

    def draw_world_annotation(self, renderer: Any, viewworld: Any) -> None:
        """Draw the current dimension state in the display pass."""
        if not self.show:
            return
        self._refresh_label()
        points = self.resolved_points
        if points is not None:
            shader = renderer.shader_world_arrow
            shader.bind()
            shader.uniform4x4("viewworld", viewworld)
            _draw_arrow(
                shader,
                self._arrow_buffer,
                start=points[0],
                end=points[1],
                transform=identity(4, dtype=float32),
                color=self.color.rgb,
                opacity=self.opacity,
                screen_size=(renderer.width(), renderer.height()),
                is_selected=self.is_selected,
            )
            shader.release()

        shader = renderer.shader_world_text
        shader.bind()
        shader.uniform4x4("viewworld", viewworld)
        _draw_text(
            shader,
            self._text_buffer,
            position=self.label_position,
            transform=identity(4, dtype=float32),
            color=self.color.rgb,
            opacity=self.opacity,
            screen_space=True,
            screen_size=(renderer.width(), renderer.height()),
            text_aspect=self.text_aspect,
            text_height=self.rendered_height,
            vertical_align=0,
            horizontal_align=0,
            is_selected=self.is_selected,
        )
        shader.release()

    def _refresh_label(self) -> None:
        label = self.display_label
        if label == getattr(self, "_label", None):
            return
        if hasattr(self, "_text_buffer"):
            _delete_text_buffer(self._text_buffer)
        self._label = label
        self._text_buffer, self.text_aspect, self.rendered_height = _make_text_buffer(label, 12.0)

    def refresh_annotation_bounds(self) -> None:
        """Recompute the dimension's resolved world-space bounds."""
        points = self.resolved_points
        if points is None:
            self._bounding_box = None
            self._bounding_box_center = None
            return
        self._bounding_box = [
            [min(a, b) for a, b in zip(points[0], points[1], strict=True)],
            [max(a, b) for a, b in zip(points[0], points[1], strict=True)],
        ]
        self._bounding_box_center = self.label_position


def _make_text_buffer(text: str, height: float) -> tuple[dict[str, int], float, float]:
    face = Face(str(FONT))
    face.set_pixel_sizes(0, RASTER_HEIGHT)
    ascender = max(1, ceil(face.size.ascender / 64))
    line_height = max(1, ceil(face.size.height / 64))
    lines = text.split("\n")

    layouts: list[list[tuple[int, int, Any]]] = []
    min_x = 0
    max_x = 1
    for line in lines:
        cursor = 0
        previous = 0
        glyphs = []
        for character in line:
            index = face.get_char_index(ord(character))
            if previous and index and face.has_kerning:
                cursor += face.get_kerning(previous, index).x >> 6
            face.load_char(character, FT_LOAD_FLAGS["FT_LOAD_RENDER"])
            glyph = face.glyph
            bitmap = glyph.bitmap
            left = cursor + glyph.bitmap_left
            glyphs.append((left, glyph.bitmap_top, array(bitmap.buffer, dtype="uint8").reshape(bitmap.rows, bitmap.width)))
            min_x = min(min_x, left)
            max_x = max(max_x, left + bitmap.width)
            cursor += glyph.advance.x >> 6
            previous = index
        max_x = max(max_x, cursor)
        layouts.append(glyphs)

    texture_width = max(1, max_x - min_x)
    texture_height = max(1, len(lines) * line_height)
    pixels = zeros((texture_height, texture_width), dtype="uint8")
    for line_index, glyphs in enumerate(layouts):
        baseline = line_index * line_height + ascender
        for left, top, bitmap in glyphs:
            if bitmap.size == 0:
                continue
            x = left - min_x
            y = baseline - top
            bottom = min(texture_height, y + bitmap.shape[0])
            right = min(texture_width, x + bitmap.shape[1])
            if bottom > y and right > x:
                pixels[y:bottom, x:right] = maximum(pixels[y:bottom, x:right], bitmap[: bottom - y, : right - x])

    texture = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_R8, texture_width, texture_height, 0, GL.GL_RED, GL.GL_UNSIGNED_BYTE, pixels)
    scale = height / RASTER_HEIGHT
    buffer = {
        "positions": make_vertex_buffer([0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0]),
        "elements": make_index_buffer([0, 1, 2, 3]),
        "text_texture": texture,
        "n": 4,
    }
    return buffer, texture_width / texture_height, texture_height * scale


def _delete_text_buffer(buffer: dict[str, int]) -> None:
    GL.glDeleteTextures(1, [buffer["text_texture"]])
    GL.glDeleteBuffers(2, [buffer["positions"], buffer["elements"]])


def _make_arrow_buffer() -> dict[str, int]:
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
    return {
        "positions": make_vertex_buffer(vertices),
        "elements": make_index_buffer(range(9)),
        "n": 9,
    }


def _delete_arrow_buffer(buffer: dict[str, int]) -> None:
    GL.glDeleteBuffers(2, [buffer["positions"], buffer["elements"]])


def _draw_text(
    shader: Any,
    buffer: dict[str, int],
    *,
    position: Point,
    transform: Any,
    color: tuple[float, float, float],
    opacity: float,
    screen_space: bool,
    screen_size: tuple[int, int],
    text_aspect: float,
    text_height: float,
    vertical_align: int,
    horizontal_align: int,
    is_selected: bool,
) -> None:
    shader.enable_attribute("position")
    shader.uniform4x4("transform", transform)
    shader.uniform1f("object_opacity", opacity)
    shader.uniform1f("is_selected", is_selected)
    shader.uniform1i("screen_space", screen_space)
    shader.uniform2f("screen_size", screen_size)
    shader.uniform2f("text_offset", (0, 0))
    shader.uniform1f("text_aspect", text_aspect)
    shader.uniform1f("text_height", text_height)
    shader.uniform3f("text_position", position)
    shader.uniform3f("text_color", color)
    shader.uniform3f("background_color", (0, 0, 0))
    shader.uniform1f("background_alpha", 0)
    shader.uniform1i("vertical_align", vertical_align)
    shader.uniform1i("horizontal_align", horizontal_align)
    shader.uniformText("text_texture", buffer["text_texture"])
    shader.bind_attribute("position", buffer["positions"])
    shader.draw_texts(elements=buffer["elements"], n=buffer["n"])
    shader.disable_attribute("position")


def _draw_arrow(
    shader: Any,
    buffer: dict[str, int],
    *,
    start: Point,
    end: Point,
    transform: Any,
    color: tuple[float, float, float],
    opacity: float,
    screen_size: tuple[int, int],
    is_selected: bool,
) -> None:
    shader.enable_attribute("position")
    shader.uniform4x4("transform", transform)
    shader.uniform2f("screen_size", screen_size)
    shader.uniform3f("start_position", start)
    shader.uniform3f("end_position", end)
    shader.uniform3f("arrow_color", color)
    shader.uniform1f("arrow_opacity", opacity)
    shader.uniform1f("line_width", 3)
    shader.uniform1f("head_length", 16)
    shader.uniform1f("head_width", 12)
    shader.uniform1f("is_selected", is_selected)
    shader.bind_attribute("position", buffer["positions"])
    shader.draw_triangles(elements=buffer["elements"], n=buffer["n"])
    shader.disable_attribute("position")


__all__ = [
    "ArrowAnnotationRenderObject",
    "DistanceDimensionRenderObject",
    "TextAnnotationRenderObject",
    "WorldAnnotationRenderObject",
]
