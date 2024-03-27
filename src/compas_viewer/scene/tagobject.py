from os import PathLike
from os import path
from typing import Literal
from typing import Optional
from typing import Union

from compas.colors import Color
from compas.geometry import Geometry
from compas.geometry import Point
from compas.scene import GeometryObject
from freetype import FT_LOAD_FLAGS
from freetype import Face
from numpy import array
from numpy import empty
from numpy import hstack
from numpy import int32, bool_
from numpy import linalg
from numpy import vstack
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
    alignment : Literal["TopLeft", "TopCenter", "TopRight", "MiddleLeft", "MiddleCenter", "MiddleRight", "BottomLeft", "BottomCenter", "BottomRight"], optional
        The alignment of the tag.
    spacing : int, optional
        The spacing of the tag.

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
    alignment : Literal["TopLeft", "TopCenter", "TopRight", "MiddleLeft", "MiddleCenter", "MiddleRight", "BottomLeft", "BottomCenter", "BottomRight"], optional
        The alignment of the tag.
    spacing : int, optional
        The spacing of the tag.
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
            and self.alignment == other.alignment
            and self.spacing == other.spacing
        )

    def __init__(
        self,
        text: str,
        position: Union[Point, tuple[float, float, float]],
        color: Color = Color(0.0, 0.0, 0.0),
        height: float = 50,
        absolute_height: bool = False,
        font: Optional[PathLike] = None,
        alignment: Literal[
            "TopLeft",
            "TopCenter",
            "TopRight",
            "MiddleLeft",
            "MiddleCenter",
            "MiddleRight",
            "BottomLeft",
            "BottomCenter",
            "BottomRight",
        ] = "BottomLeft",
        spacing: int = 1,
    ):
        super().__init__()
        self.text = text
        self.position = Point(*position)
        self.color = color
        self.height = height
        self.absolute_height = absolute_height
        self.font = font or FONT
        self.alignment = alignment
        self.spacing = spacing

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
        """Create the texture as an array of the text.

        Returns
        -------
        int
            The texture of the text.
        """

        face = Face(self.geometry.font)
        # Set basic char size to 64 pixels.
        face.set_char_size(64 * self.geometry.height)

        strings = self.geometry.text.split("\n")
        strings_array = zeros((0, 0), dtype=int32)

        for string in strings:

            # For each line
            string_array = zeros((0, 0), dtype=int32)
            for char in string:
                # Load the character.
                face.load_char(char, FT_LOAD_FLAGS["FT_LOAD_RENDER"])
                bitmap = face.glyph.bitmap
                char = array(bitmap.buffer, dtype=int32)
                char = char.reshape((bitmap.rows, bitmap.width))
                char = hstack(
                    (  
                        char,
                        zeros((char.shape[0], self.geometry.spacing * 10), dtype=int32),
                    )
                )
                # Match the height of the characters.
                if char.shape[0] > string_array.shape[0]:
                    string_array = vstack(
                        (
                            zeros((char.shape[0] - string_array.shape[0], string_array.shape[1]), dtype=int32),
                            string_array,
                        )
                    )
                elif char.shape[0] < string_array.shape[0]:
                    char = vstack((zeros((string_array.shape[0] - char.shape[0], char.shape[1]), dtype=int32),char))
                # Concatenate the characters.
                string_array = hstack((string_array, char), dtype=int32)

            # Match the width of the lines.
            if string_array.shape[1] > strings_array.shape[1]:
                strings_array = hstack(
                    (
                        strings_array,
                        zeros((strings_array.shape[0], string_array.shape[1] - strings_array.shape[1]), dtype=int32),
                    )
                )
            elif string_array.shape[1] < strings_array.shape[1]:
                string_array = hstack(
                    (
                        string_array,
                        zeros((string_array.shape[0], strings_array.shape[1] - string_array.shape[1]), dtype=int32),
                    )
                )
            # Concatenate the lines.
            strings_array = vstack((strings_array, string_array), dtype=int32)

        # Match the width and height to be the same.
        if strings_array.shape[0] > strings_array.shape[1]:
            strings_array = hstack(
                (
                    strings_array,
                    zeros((strings_array.shape[0], strings_array.shape[0] - strings_array.shape[1]), dtype=int32),
                )
            )
        elif strings_array.shape[0] < strings_array.shape[1]:
            strings_array = vstack(
                (
                    strings_array,
                    zeros((strings_array.shape[1] - strings_array.shape[0], strings_array.shape[1]), dtype=int32),
                )
            )

        # The number of characters must be a multiple of 4, as described in the OpenGL documentation.
        if strings_array.shape[0] % 4 != 0:
            strings_array = vstack(
                (
                    strings_array,
                    zeros((4 - strings_array.shape[0] % 4, strings_array.shape[1]), dtype=int32),
                )
            )

        if strings_array.shape[1] % 4 != 0:
            strings_array = hstack(
                (
                    strings_array,
                    zeros((strings_array.shape[0], 4 - strings_array.shape[1] % 4), dtype=int32),
                )
            )

        # Create the glyph texture.
        strings_buffer = strings_array.reshape((strings_array.shape[0] * strings_array.shape[1]))
        texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_R8,
            strings_array.shape[1],
            strings_array.shape[0],
            0,
            GL.GL_RED,
            GL.GL_UNSIGNED_BYTE,
            strings_buffer,
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
