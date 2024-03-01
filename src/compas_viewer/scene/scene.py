from typing import TYPE_CHECKING
from typing import Any
from typing import Optional
from typing import Union

from compas.colors import Color
from compas.data import Data
from compas.scene import Scene

from compas_viewer.configurations import SceneConfig
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
    config : :class:`compas_viewer.configurations.scene_config.SceneConfig`
        The configuration object for the scene.
    name : str, optional
        The name of the scene.

    See Also
    --------
    :class:`compas.scene.Scene`
    """

    def __new__(cls, *args, **kwargs):
        instance = super(ViewerScene, cls).__new__(cls)
        Scene.viewerinstance = instance  # type: ignore
        return instance

    def __init__(self, viewer: "Viewer", config: SceneConfig, name=None):
        super(ViewerScene, self).__init__(name=name)
        self.viewer = viewer
        self.config = config

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
        pointscolor: Optional[Union[Color, dict[Any, Color]]] = None,
        linescolor: Optional[Union[Color, dict[Any, Color]]] = None,
        facescolor: Optional[Union[Color, dict[Any, Color]]] = None,
        lineswidth: Optional[float] = None,
        pointssize: Optional[float] = None,
        opacity: Optional[float] = None,
        hide_coplanaredges: Optional[bool] = None,
        use_vertexcolors: Optional[bool] = None,
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
            It will override the value in the scene config file.
        show_lines : bool, optional
            Whether to show lines/edges of the object.
            It will override the value in the scene config file.
        show_faces : bool, optional
            Whether to show faces of the object.
            It will override the value in the scene config file.
        pointscolor : Union[:class:`compas.colors.Color`, dict[Any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the points.
            It will override the value in the scene config file.
        linescolor : Union[:class:`compas.colors.Color`, dict[Any, :class:`compas.colors.Color`], optional
            The color or the dict of colors of the lines.
            It will override the value in the scene config file.
        facescolor : Union[:class:`compas.colors.Color`, dict[Any, :class:`compas.colors.Color`], optional
            The color or the dict of colors the faces.
            It will override the value in the scene config file.
        lineswidth : float, optional
            The line width to be drawn on screen
            It will override the value in the scene config file.
        pointssize : float, optional
            The point size to be drawn on screen
            It will override the value in the scene config file.
        opacity : float, optional
            The opacity of the object.
            It will override the value in the scene config file.
        hide_coplanaredges : bool, optional
            Whether to hide the coplanar edges of the mesh.
            It will override the value in the scene config file.
        use_vertexcolors : bool, optional
            Whether to use vertex color.
            It will override the value in the scene config file.
        **kwargs : dict, optional
            The other possible parameters to be passed to the object.

        Returns
        -------
        :class:`compas_viewer.scene.ViewerSceneObject`
            The scene object.
        """

        sceneobject: ViewerSceneObject = super(ViewerScene, self).add(  # type: ignore
            item=item,
            parent=parent,
            viewer=self.viewer,
            is_selected=is_selected,
            is_visible=is_visible,
            is_locked=is_locked,
            show_points=show_points,
            show_lines=show_lines,
            show_faces=show_faces,
            pointscolor=pointscolor,
            linescolor=linescolor,
            facescolor=facescolor,
            lineswidth=lineswidth,
            pointssize=pointssize,
            opacity=opacity,
            hide_coplanaredges=hide_coplanaredges,
            use_vertexcolors=use_vertexcolors,
            config=self.config,
            **kwargs
        )

        if not is_locked:
            self.instance_colors[sceneobject.instance_color.rgb255] = sceneobject

        return sceneobject

    def clear(self, guids: Optional[Union[list[str], list[ViewerSceneObject]]] = None):
        """Clear the scene."""
        if guids is None:
            guids = self.objects

        for obj in guids:
            self.remove(obj)
            del obj
