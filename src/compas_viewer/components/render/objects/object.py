import abc
import numpy as np
import inspect

from compas.geometry import Transformation
from compas.geometry import Translation
from compas.geometry import Rotation
from compas.geometry import Scale
from compas.geometry import decompose_matrix
from compas.geometry import identity_matrix
from compas.colors import Color
from compas.data import Data

from typing import Dict, Union


ABC = abc.ABCMeta("ABC", (object,), {"__slots__": ()})

DATA_OBJECT = {}


def _get_object_cls(data):
    dtype = type(data)
    cls = None

    for type_ in inspect.getmro(dtype):
        cls = DATA_OBJECT.get(type_, None)

        if cls is not None:
            break

    if cls is None:
        raise Exception("No object is registered for this data type: {}".format(dtype))

    return cls


class Object(ABC):
    """Base object for compas_view2

    Parameters
    ----------
    data: :class:`compas.data.Data`
        A COMPAS data object.
    is_selected : bool, optional
        Whether the object is selected.
        Default to False.
    is_visible : bool, optional
        Whether to show object.
        Default to True.
    show_points : bool, optional
        Whether to show points/vertices of the object.
        Default to False.
    show_lines : bool, optional
        Whether to show lines/edges of the object.
        Default to True.
    show_faces : bool, optional
        Whether to show faces of the object.
        Default to True.
    pointcolor : Union[Color, Dict[Union[str, int], Color]], optional
        The color or the dict of colors of the points.
        Default to `compas_view2.objects.Object.default_color_points`.
    linecolor : Union[Color, Dict[Union[str, int], Color]], optional
        The color or the dict of colors of the lines.
        Default to `compas_view2.objects.Object.default_color_lines`.
    facecolor : Union[Color, Dict[Union[str, int], Color]], optional
        The color or the dict of colors the faces.
        Default to `compas_view2.objects.Object.default_color_faces`.
    linewidth : int, optional
        The line width to be drawn on screen
        Default to 1.
    pointsize : int, optional
        The point size to be drawn on screen
        Default to 10.
    opacity : float, optional
        The opacity of the object.
        Default to 1.0.
    **kwargs : dict, optional
        Additional visualization options for specific objects.

    Attributes
    ----------
    is_selected : bool
        Whether the object is selected.
    is_visible : bool
        Whether to show object.
    show_points : bool
        Whether to show points/vertices of the object.
    show_lines : bool
        Whether to show lines/edges of the object.
    show_faces : bool
        Whether to show faces of the object.
    pointcolor : :class:`compas.color.Color`
        The color of the points.
    linecolor : :class:`compas.color.Color`
        The color of the lines.
    facecolor : :class:`compas.color.Color`
        The color of the faces.
    pointcolors : Dict[Union[str, int], Color]
        The color dict of individual points.
    linecolors : Dict[Union[str, int], Color]
        The color dict of individual lines.
    facecolors : Dict[Union[str, int], Color]
        The color dict of individual faces.
    linewidth : int
        The line width to be drawn on screen.
    pointsize : int
        The point size to be drawn on screen.
    opacity : float
        The opacity of the object.
    background : bool
        Whether the object is drawn on the backgound with depth test disabled.
    bounding_box : :class:`numpy.array`, read-only
        The min and max corners of object bounding box, as a numpy array of shape (2, 3).
    bounding_box_center : :class:`numpy.array`, read-only
        The center of object bounding box, as a numpy array of shape (3,).
    matrix : :class:`numpy.array`
        The transformation matrix of the object.
    translation : :class:`numpy.array`
        The translation vector of the object.
    rotation : :class:`numpy.array`
        The euler rotation vector of the object.
    scale : :class:`numpy.array`
        The scale vector of the object.
    properties : list, read-only
        The list of object-specific properties.
    otype : class
        The data class of the object.

    """

    default_color_points = Color(0.2, 0.2, 0.2)
    default_color_lines = Color(0.4, 0.4, 0.4)
    default_color_faces = Color(0.8, 0.8, 0.8)

    @staticmethod
    def register(dtype, otype):
        """Register an object class to its corrensponding data type"""
        DATA_OBJECT[dtype] = otype

    @staticmethod
    def build(data, **kwargs):
        """Build an object class according to its corrensponding data type"""
        try:
            obj = _get_object_cls(data)(data, **kwargs)
        except KeyError:
            raise TypeError("Type {} is not supported by the viewer.".format(type(data)))
        return obj

    def __init__(
        self,
        data: Data,
        app=None,
        name: str = None,
        is_selected: bool = False,
        is_visible: bool = True,
        show_points: bool = False,
        show_lines: bool = True,
        show_faces: bool = True,
        pointcolor: Union[Color, Dict[Union[str, int], Color]] = None,
        linecolor: Union[Color, Dict[Union[str, int], Color]] = None,
        facecolor: Union[Color, Dict[Union[str, int], Color]] = None,
        linewidth: int = 1,
        pointsize: int = 10,
        opacity: float = 1.0,
    ):
        self._data = data
        self._app = app
        self.name = name or str(self)
        self.is_selected = is_selected
        self.is_visible = is_visible
        self.parent = None
        self._children = set()

        self.show_points = show_points
        self.show_lines = show_lines
        self.show_faces = show_faces

        if isinstance(pointcolor, dict):
            self.pointcolor = Color(*self.default_color_points)
            self.pointcolors = pointcolor
        else:
            self.pointcolor = Color(*(pointcolor or self.default_color_points))
            self.pointcolors = {}
        if isinstance(linecolor, dict):
            self.linecolor = Color(*self.default_color_lines)
            self.linecolors = linecolor
        else:
            self.linecolor = Color(*(linecolor or self.default_color_lines))
            self.linecolors = {}
        if isinstance(facecolor, dict):
            self.facecolor = Color(*self.default_color_faces)
            self.facecolors = facecolor
        else:
            self.facecolor = Color(*(facecolor or self.default_color_faces))
            self.facecolors = {}

        self.linewidth = linewidth
        self.pointsize = pointsize
        self.opacity = opacity
        self.background = False

        self._instance_color = None
        self._translation = [0.0, 0.0, 0.0]
        self._rotation = [0.0, 0.0, 0.0]
        self._scale = [1.0, 1.0, 1.0]
        self._transformation = Transformation()
        self._matrix_buffer = None

        self._bounding_box = None
        self._bounding_box_center = None
        self._is_collection = False

    @property
    def bounding_box(self):
        return self._bounding_box

    @property
    def bounding_box_center(self):
        return self._bounding_box_center

    @property
    def otype(self):
        return DATA_OBJECT[self._data.__class__]

    @property
    def DATA_OBJECT(self):
        return DATA_OBJECT

    @abc.abstractmethod
    def init(self):
        pass

    @abc.abstractmethod
    def draw(self, shader):
        pass

    def create(self):
        pass

    @property
    def properties(self):
        return None

    @property
    def children(self):
        return self._children

    def add(self, item, **kwargs):
        if isinstance(item, Object):
            obj = item
        else:
            obj = self._app.add(item, **kwargs)
        self._children.add(obj)
        obj.parent = self

        if self._app.dock_slots["sceneform"] and self._app.view.isValid():
            self._app.dock_slots["sceneform"].update()
        return obj

    def remove(self, obj):
        obj.parent = None
        self._children.remove(obj)

    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, vector):
        self._translation[0] = vector[0]
        self._translation[1] = vector[1]
        self._translation[2] = vector[2]

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, angles):
        self._rotation[0] = angles[0]
        self._rotation[1] = angles[1]
        self._rotation[2] = angles[2]

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, factors):
        self._scale[0] = factors[0]
        self._scale[1] = factors[1]
        self._scale[2] = factors[2]

    def _update_matrix(self):
        """Update the matrix from object's translation, rotation and scale"""
        if (not self.parent or self.parent._matrix_buffer is None) and (
            self.translation == [0, 0, 0] and self.rotation == [0, 0, 0] and self.scale == [1, 1, 1]
        ):
            self._transformation.matrix = identity_matrix(4)
            self._matrix_buffer = None
        else:
            T1 = Translation.from_vector(self.translation)
            R1 = Rotation.from_euler_angles(self.rotation)
            S1 = Scale.from_factors(self.scale)
            M = T1 * R1 * S1
            self._transformation.matrix = M.matrix
            self._matrix_buffer = np.array(self.matrix_world).flatten()

        if self.children:
            for child in self.children:
                child._update_matrix()

    @property
    def transformation(self):
        return self._transformation

    @property
    def transformation_world(self):
        """Get the updated matrix from object's translation, rotation and scale"""
        if self.parent:
            return self.parent.transformation_world * self.transformation
        else:
            return self.transformation

    @property
    def matrix(self):
        """Get the updated matrix from object's translation, rotation and scale"""
        return self.transformation.matrix

    @property
    def matrix_world(self):
        """Get the updated matrix from object's translation, rotation and scale"""
        return self.transformation_world.matrix

    @matrix.setter
    def matrix(self, matrix):
        """Set the object's translation, rotation and scale from given matrix, and update object's matrix"""
        scale, _, rotation, tranlation, _ = decompose_matrix(matrix)
        self.translation = tranlation
        self.rotation = rotation
        self.scale = scale
        self._update_matrix()
