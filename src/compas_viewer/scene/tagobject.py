from math import ceil
from pathlib import Path
from typing import Any
from typing import Literal
from typing import Self
from typing import cast

from freetype import FT_LOAD_FLAGS
from freetype import Face
from numpy import array
from numpy import maximum
from numpy import zeros
from OpenGL import GL

from compas.colors import Color
from compas.geometry import Geometry
from compas.geometry import Point
from compas.geometry import Transformation
from compas.geometry import Vector
from compas.scene import GeometryObject
from compas_viewer import HERE
from compas_viewer.gl import make_index_buffer
from compas_viewer.gl import make_vertex_buffer

from .sceneobject import ViewerSceneObject

FONT = HERE / "assets" / "fonts" / "FreeSans.ttf"
RASTER_HEIGHT = 48

type HorizontalAlignment = Literal["left", "center", "right"]
type VerticalAlignment = Literal["bottom", "center", "top"]


class Tag(Geometry):
    """Camera-facing text annotation anchored to a 3D point.

    Parameters
    ----------
    text
        Annotation text. Newline characters create multiple lines.
    position
        Anchor point in world coordinates.
    color
        Text color.
    height
        Text line height, in screen pixels by default or world units when
        ``absolute_height`` is enabled.
    absolute_height
        Draw with a constant world-space height instead of a constant
        screen-space height.
    font
        Path to a TrueType or OpenType font.
    vertical_align
        Vertical alignment relative to the anchor point.
    horizontal_align
        Horizontal alignment relative to the anchor point.
    backgroundcolor
        Optional background color. Its alpha controls background opacity.
    padding
        Padding around the text in the same units as ``height``.
    offset
        Two-dimensional offset from the anchor in the same units as
        ``height``.
    line_spacing
        Multiplier applied to the font's default line spacing.

    """

    def __init__(
        self,
        text: str,
        position: Point | tuple[float, float, float],
        color: Color | None = None,
        height: float = 50,
        absolute_height: bool = False,
        font: str | Path | None = None,
        vertical_align: VerticalAlignment = "bottom",
        horizontal_align: HorizontalAlignment = "left",
        backgroundcolor: Color | None = None,
        padding: float = 0,
        offset: tuple[float, float] = (0, 0),
        line_spacing: float = 1.0,
    ) -> None:
        super().__init__()
        if height <= 0:
            raise ValueError("Annotation height must be positive.")
        if padding < 0:
            raise ValueError("Annotation padding cannot be negative.")
        if line_spacing <= 0:
            raise ValueError("Annotation line spacing must be positive.")
        if vertical_align not in {"bottom", "center", "top"}:
            raise ValueError(f"Unsupported vertical alignment: {vertical_align!r}.")
        if horizontal_align not in {"left", "center", "right"}:
            raise ValueError(f"Unsupported horizontal alignment: {horizontal_align!r}.")

        self.text = str(text)
        self.position = Point(position[0], position[1], position[2])
        self.color = color or Color.black()
        self.height = float(height)
        self.absolute_height = absolute_height
        self.font = Path(font or FONT).expanduser().resolve()
        self.vertical_align = vertical_align
        self.horizontal_align = horizontal_align
        self.backgroundcolor = backgroundcolor
        self.padding = float(padding)
        self.offset = (float(offset[0]), float(offset[1]))
        self.line_spacing = float(line_spacing)

    @property
    def __data__(self) -> dict[str, Any]:
        """dict[str, Any]: Serializable annotation data."""
        return {
            "text": self.text,
            "position": self.position,
            "color": self.color,
            "height": self.height,
            "absolute_height": self.absolute_height,
            "font": str(self.font),
            "vertical_align": self.vertical_align,
            "horizontal_align": self.horizontal_align,
            "backgroundcolor": self.backgroundcolor,
            "padding": self.padding,
            "offset": self.offset,
            "line_spacing": self.line_spacing,
        }

    @classmethod
    def __from_data__(cls, data: dict[str, Any]) -> Self:
        """Construct an annotation from serialized data."""
        return cls(**data)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Tag) and self.__data__ == other.__data__

    def transform(self, transformation: Transformation) -> None:
        """Transform the annotation anchor.

        Parameters
        ----------
        transformation
            Transformation applied to the anchor point.

        """
        self.position.transform(transformation)


class TagObject(ViewerSceneObject, GeometryObject):
    """Render a text annotation as a camera-facing billboard."""

    VERTICAL_ALIGN = {"top": 1, "center": 0, "bottom": -1}
    HORIZONTAL_ALIGN = {"left": -1, "center": 0, "right": 1}

    @property
    def tag(self) -> Tag:
        """Tag: The typed annotation geometry."""
        return cast(Tag, self.geometry)

    def init(self) -> None:
        """Create the annotation's OpenGL resources."""
        self.make_buffers()
        self._update_bounding_box([self.tag.position])
        self._inited = True

    def update(self, update_transform: bool = True, update_data: bool = False) -> None:
        """Update the annotation after its geometry changes.

        Parameters
        ----------
        update_transform
            Whether to redraw after a transformation change.
        update_data
            Whether to rebuild the text texture and bounds.

        """
        if update_data:
            self.make_buffers()
            self._update_bounding_box([self.tag.position])
        if update_transform or update_data:
            self.viewer.renderer.update()

    def make_buffers(self) -> None:
        """Create the annotation quad and text texture."""
        if hasattr(self, "_text_buffer"):
            GL.glDeleteTextures(1, [self._text_buffer["text_texture"]])

        positions = [0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 0]
        texture, aspect, rendered_height = self.make_text_texture()
        self.text_aspect = aspect
        self.rendered_height = rendered_height
        self._text_buffer = {
            "positions": make_vertex_buffer(positions),
            "elements": make_index_buffer([0, 1, 2, 3]),
            "text_texture": texture,
            "n": 4,
        }

    def make_text_texture(self) -> tuple[int, float, float]:
        """Rasterize multiline text and upload it as an OpenGL texture."""
        tag = cast(Tag, self.geometry)
        face = Face(str(tag.font))
        face.set_pixel_sizes(0, RASTER_HEIGHT)

        ascender = max(1, ceil(face.size.ascender / 64))
        natural_line_height = max(1, ceil(face.size.height / 64))
        line_height = max(1, ceil(natural_line_height * tag.line_spacing))
        lines = tag.text.split("\n")
        padding = ceil(tag.padding / tag.height * RASTER_HEIGHT)

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

        text_width = max_x - min_x
        texture_width = max(1, text_width + 2 * padding)
        texture_height = max(1, len(lines) * line_height + 2 * padding)
        pixels = zeros((texture_height, texture_width), dtype="uint8")

        for line_index, glyphs in enumerate(layouts):
            baseline = padding + line_index * line_height + ascender
            for left, top, bitmap in glyphs:
                if bitmap.size == 0:
                    continue
                x = padding + left - min_x
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

        scale = tag.height / RASTER_HEIGHT
        return texture, texture_width / texture_height, texture_height * scale

    def draw_annotation(self, shader: Any, camera_position: Point | Vector, width: int, height: int) -> None:
        """Draw the annotation.

        Parameters
        ----------
        shader
            Shader configured for annotation rendering.
        camera_position
            Current camera position. Retained for renderer API compatibility.
        width
            Viewport width in pixels.
        height
            Viewport height in pixels.

        """
        if not self.show:
            return
        shader.enable_attribute("position")
        if self.worldtransformation is not None:
            shader.uniform4x4("transform", self.worldtransformation.matrix)
        background = self.tag.backgroundcolor or Color(0, 0, 0, 0)
        shader.uniform1f("object_opacity", self.opacity)
        shader.uniform1f("is_selected", self.is_selected)
        shader.uniform1i("screen_space", not self.tag.absolute_height)
        shader.uniform2f("screen_size", (width, height))
        shader.uniform2f("text_offset", self.tag.offset)
        shader.uniform1f("text_aspect", self.text_aspect)
        shader.uniform1f("text_height", self.rendered_height)
        shader.uniform3f("text_position", self.tag.position)
        shader.uniform3f("text_color", self.tag.color.rgb)
        shader.uniform3f("background_color", background.rgb)
        shader.uniform1f("background_alpha", background.a)
        shader.uniform1i("vertical_align", self.VERTICAL_ALIGN[self.tag.vertical_align])
        shader.uniform1i("horizontal_align", self.HORIZONTAL_ALIGN[self.tag.horizontal_align])
        shader.uniformText("text_texture", self._text_buffer["text_texture"])
        shader.bind_attribute("position", self._text_buffer["positions"])
        shader.draw_texts(elements=self._text_buffer["elements"], n=self._text_buffer["n"])
        shader.uniform1f("object_opacity", 1)
        shader.disable_attribute("position")

    def _read_points_data(self) -> None:
        return None

    def _read_lines_data(self) -> None:
        return None

    def _read_frontfaces_data(self) -> None:
        return None

    def _read_backfaces_data(self) -> None:
        return None


# Descriptive public name for new code. ``Tag`` remains available for
# compatibility with existing scenes and serialized data.
TextAnnotation = Tag
