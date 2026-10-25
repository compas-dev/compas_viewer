from collections.abc import Generator
from random import randint
from random import seed
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from compas.colors import Color
from compas.data import Data
from compas.scene import Scene
from compas.scene import SceneObject

from .group import Group
from .sceneobject import ViewerSceneObject

if TYPE_CHECKING:
    from compas_viewer import Viewer


def instance_colors_generator(i: int = 0) -> Generator[tuple[int, int, int], None, None]:
    """Generate non-repeating pseudo-random instance colors.

    Parameters
    ----------
    i
        Seed for the random number generator.

    Yields
    ------
    tuple[int, int, int]
        RGB colors with components in the range 0--254.

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
    """Manage viewer scene objects and their instance-selection colors.

    Parameters
    ----------
    name
        Name of the scene.
    context
        Scene-object registration context.

    """

    def __init__(self, name: str = "ViewerScene", context: str = "Viewer") -> None:
        super().__init__(name=name, context=context)
        self.instance_colors: dict[tuple[int, int, int], ViewerSceneObject] = {}
        self._instance_colors_generator = instance_colors_generator()

    @property
    def viewer(self) -> "Viewer":
        from compas_viewer import Viewer

        return Viewer()

    # TODO: These fixed kwargs could be moved to COMPAS core.
    def add(
        self,
        item: Data | SceneObject,
        parent: SceneObject | None = None,
        is_selected: bool = False,
        show: bool = True,
        show_points: bool | None = None,
        show_lines: bool | None = None,
        show_faces: bool | None = None,
        vertexcolor: Color | dict[Any, Color] | None = None,
        pointcolor: Color | dict[Any, Color] | None = None,
        linecolor: Color | dict[Any, Color] | None = None,
        facecolor: Color | dict[Any, Color] | None = None,
        surfacecolor: Color | dict[Any, Color] | None = None,
        linewidth: float | None = None,
        pointsize: float | None = None,
        opacity: float | None = None,
        hide_coplanaredges: bool | None = None,
        use_vertexcolors: bool | None = None,
        v: int | None = None,
        u: int | None = None,
        **kwargs: Any,
    ) -> ViewerSceneObject:
        """Add an item to the scene.

        Parameters
        ----------
        item
            Geometry, data structure, scene object, or collection to add.
        parent
            The parent of the item.
        is_selected : bool, optional
            Whether the object is selected.
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
            The resolution in the V direction. By default, use the geometry's
            existing resolution.
        u : int, optional
            The resolution in the U direction. By default, use the geometry's
            existing resolution.
        **kwargs
            Additional options passed to the scene-object constructor.

        Returns
        -------
        ViewerSceneObject
            The scene object.

        """
        edgecolor = kwargs.pop("edgecolor", linecolor)

        sceneobject = super().add(
            item=cast(Data, item),
            parent=parent,
            is_selected=is_selected,
            show=show,
            show_points=show_points,
            show_lines=show_lines,
            show_faces=show_faces,
            pointcolor=pointcolor,
            vertexcolor=vertexcolor or pointcolor,
            linecolor=linecolor,
            edgecolor=edgecolor,
            facecolor=facecolor,
            surfacecolor=surfacecolor or facecolor,
            linewidth=linewidth,
            pointsize=pointsize,
            opacity=opacity,
            hide_coplanaredges=hide_coplanaredges,
            use_vertexcolors=use_vertexcolors,
            v=v,
            u=u,
            **kwargs,
        )

        if self.viewer.running:
            self.viewer.renderer.rebuild_buffers()
            self.viewer.renderer.update()
            self.viewer.ui.sidebar.update()

        return cast(ViewerSceneObject, sceneobject)

    def add_group(self, name: str = "Group", parent: SceneObject | None = None, **kwargs: Any) -> Group:
        """Add a group to the scene.

        Parameters
        ----------
        name
            The name of the group.
        parent
            The parent of the group.
        **kwargs
            The other possible parameters to be passed to the group.

        Returns
        -------
        Group
            The group.

        """
        group = Group(name=name, **kwargs)
        self.add(group, parent=parent)
        return group

    def remove(self, sceneobject: SceneObject, rebuild_buffers: bool = True) -> None:
        """Remove a scene object from the scene.

        Parameters
        ----------
        sceneobject
            The scene object to remove.
        rebuild_buffers
            Whether to rebuild the buffers.
            Default to True.

        """
        super().remove(sceneobject)

        if self.viewer.running and rebuild_buffers:
            self.viewer.renderer.rebuild_buffers()
            self.viewer.renderer.update()
            self.viewer.ui.sidebar.update()
