from random import randint
from random import seed
from typing import Any
from typing import Generator
from typing import Optional
from typing import Union

from compas.colors import Color
from compas.datastructures import Datastructure
from compas.geometry import Geometry
from compas.scene import Scene

from .sceneobject import ViewerSceneObject


def instance_colors_generator(i: int = 0) -> Generator:
    """
    Generate a set of non-repetitive random colors for instance colors.

    Parameters
    ----------
    i : int, optional
        Seed for the random number generator. Default is ``0``.

    Yields
    ------
    tuple of int
        A tuple of three integers representing the RGB color of the instance.
    """

    dim = 255
    seed(i)
    existed = []

    while True:
        n = randint(0, dim**3)

        if n in existed:
            continue

        existed.append(n)

        r = n // dim**2
        g = (n - r * dim**2) // dim
        b = n - r * dim**2 - g * dim

        yield (r, g, b)


class ViewerScene(Scene):
    """The ViewerScene class is a wrapper for the compas.Scene class,
    providing additional functionality for the viewer.

    Parameters
    ----------
    viewer : :class:`compas_viewer.Viewer`
        The viewer object.
    name : str, optional
        The name of the scene.
    context : str, optional
        The context of the scene.

    See Also
    --------
    :class:`compas.scene.Scene`
    """

    def __init__(self, name: str = "ViewerScene", context: str = "Viewer"):
        super().__init__(name=name, context=context)

        #  Primitive
        self.objects: list[ViewerSceneObject]

        #  Selection
        self.instance_colors: dict[tuple[int, int, int], ViewerSceneObject] = {}
        self._instance_colors_generator = instance_colors_generator()

    # TODO: These fixed kwargs could be moved to COMPAS core.
    def add(
        self,
        item: Union[Geometry, Datastructure, ViewerSceneObject],
        parent: Optional[ViewerSceneObject] = None,
        is_selected: bool = False,
        is_locked: bool = False,
        show: bool = True,
        show_points: Optional[bool] = None,
        show_lines: Optional[bool] = None,
        show_faces: Optional[bool] = None,
        pointcolor: Optional[Union[Color, dict[Any, Color]]] = None,
        linecolor: Optional[Union[Color, dict[Any, Color]]] = None,
        facecolor: Optional[Union[Color, dict[Any, Color]]] = None,
        linewidth: Optional[float] = None,
        pointsize: Optional[float] = None,
        opacity: Optional[float] = None,
        hide_coplanaredges: Optional[bool] = None,
        use_vertexcolors: Optional[bool] = None,
        v: int = 16,
        u: int = 16,
        **kwargs,
    ) -> ViewerSceneObject:
        """
        Add an item to the scene.
        This function is inherent from :class:`compas.scene.Scene` with additional functionalities.

        Parameters
        ----------
        item : Union[:class:`compas.geometry.Geometry`, :class:`compas.datastructures.Datastructure`,
            :class:`compas_viewer.scene.ViewerSceneObject`]
            The geometry to add to the scene.
        parent : :class:`compas_viewer.scene.ViewerSceneObject`, optional
            The parent of the item.
        is_selected : bool, optional
            Whether the object is selected.
            Default to False.
        is_locked : bool, optional
            Whether the object is locked (not selectable).
            Default to False.
        show : bool, optional
            Whether to show object.
            Default to True.
        show_points : bool, optional
            Whether to show points/vertices of the object.
        show_lines : bool, optional
            Whether to show lines/edges of the object.
        show_faces : bool, optional
            Whether to show faces of the object.
        pointcolor : Union[:class:`compas.colors.Color`, dict[Any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the points/vertices of object.
        linecolor : Union[:class:`compas.colors.Color`, dict[Any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the lines/edges of object.
        facecolor : Union[:class:`compas.colors.Color`, dict[Any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the faces of object.
        linewidth : float, optional
            The line width to be drawn on screen
        pointsize : float, optional
            The point size to be drawn on screen
        opacity : float, optional
            The opacity of the object.
        hide_coplanaredges : bool, optional
            Whether to hide the coplanar edges of the mesh.
        use_vertexcolors : bool, optional
            Whether to use vertex color.
        v : int, optional
            The number of vertices in the u-direction of non-OCC geometries. Default is 16.
        u : int, optional
            The number of vertices in the v-direction of non-OCC geometries. Default is 16.
        **kwargs : dict, optional
            The other possible parameters to be passed to the object.

        Returns
        -------
        :class:`compas_viewer.scene.ViewerSceneObject`
            The scene object.
        """

        sceneobject: ViewerSceneObject = super().add(  # type: ignore
            item=item,
            parent=parent,
            is_selected=is_selected,
            show=show,
            is_locked=is_locked,
            show_points=show_points,
            show_lines=show_lines,
            show_faces=show_faces,
            pointcolor=pointcolor,
            linecolor=linecolor,
            facecolor=facecolor,
            linewidth=linewidth,
            pointsize=pointsize,
            opacity=opacity,
            hide_coplanaredges=hide_coplanaredges,
            use_vertexcolors=use_vertexcolors,
            v=v,
            u=u,
            **kwargs,
        )

        return sceneobject
