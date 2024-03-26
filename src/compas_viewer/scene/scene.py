from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from typing import Union

from compas.colors import Color
from compas.data import Data
from compas.scene import Scene

from compas_viewer.utilities import instance_colors_generator

from .sceneobject import ViewerSceneObject

if TYPE_CHECKING:
    from compas_viewer import Viewer


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

    def __init__(self, viewer: "Viewer", name: str, context: str):
        super(ViewerScene, self).__init__(name=name, context=context)
        self.viewer = viewer

        #  Primitive
        self.objects: list[ViewerSceneObject]

        #  Selection
        self.instance_colors: dict[tuple[int, int, int], ViewerSceneObject] = {}
        self._instance_colors_generator = instance_colors_generator()

    def add(
        self,
        item: Data,
        parent: Optional[ViewerSceneObject] = None,
        is_selected: bool = False,
        is_locked: bool = False,
        is_visible: bool = True,
        show_points: Optional[bool] = None,
        show_lines: Optional[bool] = None,
        show_faces: Optional[bool] = None,
        pointcolor: Optional[Color] = None,
        linecolor: Optional[Color] = None,
        surfacecolor: Optional[Color] = None,
        vertexcolor: Optional[Union[Color, dict[Any, Color]]] = None,
        edgecolor: Optional[Union[Color, dict[Any, Color]]] = None,
        facecolor: Optional[Union[Color, dict[Any, Color]]] = None,
        lineswidth: Optional[float] = None,
        pointssize: Optional[float] = None,
        opacity: Optional[float] = None,
        hide_coplanaredges: Optional[bool] = None,
        use_vertexcolors: Optional[bool] = None,
        v: int = 16,
        u: int = 16,
        **kwargs
    ) -> ViewerSceneObject:
        """
        Add an item to the scene.
        This function is inherent from :class:`compas.scene.Scene` with additional functionalities.

        Parameters
        ----------
        item : Union[:class:`compas.geometry.Geometry`, :class:`compas.datastructures.Mesh`]
            The geometry to add to the scene.
        parent : :class:`compas_viewer.scene.ViewerSceneObject`, optional
            The parent of the item.
        is_selected : bool, optional
            Whether the object is selected.
            Default to False.
        is_locked : bool, optional
            Whether the object is locked (not selectable).
            Default to False.
        is_visible : bool, optional
            Whether to show object.
            Default to True.
        show_points : bool, optional
            Whether to show points/vertices of the object.
        show_lines : bool, optional
            Whether to show lines/edges of the object.
        show_faces : bool, optional
            Whether to show faces of the object.
        pointcolor : :class:`compas.colors.Color`, optional
            The single color of colors of the points in the COMPAS Geometry.
        linecolor : :class:`compas.colors.Color`, optional
            The single color of colors of the lines in the COMPAS Geometry.
        surfacecolor : :class:`compas.colors.Color`, optional
            The single color of colors the surfaces in the COMPAS Geometry.
        vertexcolor : Union[:class:`compas.colors.Color`, dict[Any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the vertices in the COMPAS Mesh.
        edgecolor : Union[:class:`compas.colors.Color`, dict[Any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the edges in the COMPAS Mesh.
        facecolor : Union[:class:`compas.colors.Color`, dict[Any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the faces in the COMPAS Mesh.
        lineswidth : float, optional
            The line width to be drawn on screen
        pointssize : float, optional
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
            viewer=self.viewer,
            is_selected=is_selected,
            is_visible=is_visible,
            is_locked=is_locked,
            show_points=show_points,
            show_lines=show_lines,
            show_faces=show_faces,
            pointcolor=pointcolor,
            linecolor=linecolor,
            facecolor=facecolor,
            surfacecolor=surfacecolor,
            vertexcolor=vertexcolor,
            edgecolor=edgecolor,
            lineswidth=lineswidth,
            pointssize=pointssize,
            opacity=opacity,
            hide_coplanaredges=hide_coplanaredges,
            use_vertexcolors=use_vertexcolors,
            v=v,
            u=u,
            **kwargs,
        )

        return sceneobject
