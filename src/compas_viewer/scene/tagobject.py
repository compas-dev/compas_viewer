from os import PathLike
from os import path
from typing import Optional
from typing import Union

from compas.colors import Color
from compas.geometry import Geometry
from compas.geometry import Point
from compas.scene import GeometryObject
from freetype import FT_LOAD_FLAGS
from freetype import Face
from numpy import array
from numpy import linalg
from numpy import zeros
from OpenGL import GL

from compas_viewer import HERE
from compas_viewer.gl import make_index_buffer
from compas_viewer.gl import make_vertex_buffer

from .sceneobject import ViewerSceneObject

FONT = path.join(HERE, "configurations", "default_config", "FreeSans.ttf")


class Tag(Geometry):
    """The geometry class of the tag. A tag is a text label that is always facing the camera.

    Parameters
    ----------
    text : str
        The text of the tag.
    position : Union[:class:`compas.geometry.Point`, tuple[float, float, float]]
        The position of the tag.
    color : :class:`compas.colors.Color`, optional
        The color of the tag.
        Default is black.
    height : float, optional
        The height of the tag.
        Default is 50.
    absolute_height : bool, optional
        If True, the height of the tag is calculated based on the distance between the tag and the camera.
        Default is False.
    font : :class:`os.PathLike`, optional
        The font of the tag.
        Default is FreeSans.ttf in the default config folder.

    Attributes
    ----------
    text : str
        The text of the tag.
    position : :class:`compas.geometry.Point`
        The position of the tag.
    color : :class:`compas.colors.Color`
        The color of the tag.
    height : float
        The height of the tag.
    absolute_height : bool
        If True, the height of the tag is calculated based on the distance between the tag and the camera.
    font : :class:`os.PathLike`
        The font of the tag.
    """

    def __eq__(self, other):
        return (
            isinstance(other, Tag)
            and self.text == other.text
            and self.position == other.position
            and self.color == other.color
            and self.height == other.height
            and self.absolute_height == other.absolute_height
            and self.font == other.font
        )

    def __init__(
        self,
        text: str,
        position: Union[Point, tuple[float, float, float]],
        color: Color = Color(0.0, 0.0, 0.0),
        height: float = 50,
        absolute_height: bool = False,
        font: Optional[PathLike] = None,
    ):
        super().__init__()
        self.text = text
        self.position = Point(*position)
        self.color = color
        self.height = height
        self.absolute_height = absolute_height
        self.font = font or FONT

    def transform(self, transformation):
        """Transform the tag.

        Parameters
        ----------
        transformation : :class:`compas.geometry.Transformation`
            The transformation used to transform the geometry.

        """
        self.position.transform(transformation)


class TagObject(ViewerSceneObject, GeometryObject):
    """
    The scene object of the viewer tag geometry.
    Unlike :class:`compas_viewer.scene.TextObject`, tag object is a sprite always facing the camera.

    Parameters
    ----------
    tag : :class:`compas_viewer.scene.Tag`
        The tag geometry.
    **kwargs : dict, optional
        Additional options for the :class:`compas_viewer.scene.ViewerSceneObject`.

    See Also
    --------
    :class:`compas_viewer.scene.Tag`
    """

    def __init__(self, tag: Tag, **kwargs):
        super().__init__(geometry=tag, **kwargs)

    def make_buffers(self):
        self._text_buffer = {
            "positions": make_vertex_buffer(self.geometry.position),
            "elements": make_index_buffer([0]),
            "text_texture": self.make_text_texture(),
            "n": 1,
        }

    def make_text_texture(self):
        face = Face(self.geometry.font)
        # the size is specified in 1/64 pixel
        face.set_char_size(64 * 48)

        text = self.geometry.text

        space_width = 12
        spacing = 4
        total_width = 0
        max_height = 0
        max_y_offset = 0
        for c in text:
            if c == " ":
                total_width += space_width + spacing
                continue
            face.load_char(c, FT_LOAD_FLAGS["FT_LOAD_RENDER"])
            glyph = face.glyph
            bitmap = glyph.bitmap
            total_width += bitmap.width + spacing
            max_height = max(max_height, bitmap.rows)
            max_y_offset = max(max_y_offset, bitmap.rows - glyph.bitmap_top)

        # The width and height of the texture must be a multiple of 4
        total_width = (total_width + 3) // 4 * 4
        # The height is doubled because the text is rendered in the middle of the texture
        max_height = (max_height * 2 + 3) // 4 * 4

        string_buffer = zeros(shape=(max_height, total_width), dtype="uint8")

        max_y_offset += 1

        offset = 0
        for c in text:
            if c == " ":
                offset += space_width + spacing
                continue

            face.load_char(c, FT_LOAD_FLAGS["FT_LOAD_RENDER"])
            glyph = face.glyph
            bitmap = glyph.bitmap

            char = array(bitmap.buffer)
            char = char.reshape((bitmap.rows, bitmap.width))

            y_offset = bitmap.rows - glyph.bitmap_top
            string_buffer[
                -char.shape[0] - max_y_offset + y_offset : -max_y_offset + y_offset,  # noqa: E203
                offset : offset + char.shape[1],  # noqa: E203
            ] = char

            offset += char.shape[1] + spacing

        # create glyph texture
        texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_R8,
            total_width,
            max_height,
            0,
            GL.GL_RED,
            GL.GL_UNSIGNED_BYTE,
            string_buffer,
        )
        return texture

    def _calculate_text_height(self, camera_position):
        if self.geometry.absolute_height:
            return int(
                (10 * self.geometry.height)
                / float(
                    linalg.norm(
                        array(self.geometry.position) - array([camera_position.x, camera_position.y, camera_position.z])
                    )
                )
            )

        else:
            return self.geometry.height

    def draw(self, shader, camera_position):
        """Draw the object from its buffers"""
        shader.enable_attribute("position")
        if self.worldtransformation is not None:
            shader.uniform4x4("transform", self.worldtransformation.matrix)
        shader.uniform1f("object_opacity", self.opacity)
        shader.uniform1i("text_height", self._calculate_text_height(camera_position))
        shader.uniform1i("text_num", len(self.geometry.text))
        shader.uniform3f("text_color", self.geometry.color)
        shader.uniformText("text_texture", self._text_buffer["text_texture"])
        shader.bind_attribute("position", self._text_buffer["positions"])
        shader.draw_texts(elements=self._text_buffer["elements"], n=self._text_buffer["n"])
        shader.uniform1i("is_text", 0)
        shader.uniform1f("object_opacity", 1)
        shader.disable_attribute("position")

    def _read_points_data(self):
        return None

    def _read_lines_data(self):
        return None

    def _read_frontfaces_data(self):
        return None

    def _read_backfaces_data(self):
        return None
