from collections.abc import Generator
from random import randint
from random import seed
from typing import TYPE_CHECKING
from typing import Any
from uuid import UUID

from compas.colors import Color
from compas.data import Data
from compas.scene import Scene
from compas.scene import SceneAnnotation
from compas.scene import SceneNode
from compas.scene import SceneObject

from .sceneobject import ViewerSceneObject

if TYPE_CHECKING:
    from compas.scene import ArrowAnnotation
    from compas.scene import DimensionStyle
    from compas.scene import DistanceDimension
    from compas.scene import TextAnnotation
    from compas_viewer import Viewer

    from .annotationobject import WorldAnnotationRenderObject


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

    def __init__(
        self,
        name: str = "ViewerScene",
        context: str | None = "Viewer",
        *,
        _detect_context: bool = True,
        _objects: dict[UUID, SceneObject] | None = None,
        _root: SceneNode | None = None,
        _annotations: list[SceneAnnotation] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            context=context,
            _detect_context=_detect_context,
            _objects=_objects,
            _root=_root,
            _annotations=_annotations,
        )
        self.render_objects: dict[UUID, ViewerSceneObject] = {}
        self.annotation_render_objects: dict[UUID, WorldAnnotationRenderObject] = {}
        self.instance_colors: dict[tuple[int, int, int], SceneObject] = {}
        self._instance_colors_generator = instance_colors_generator()
        self._viewer: Viewer | None = None

    @property
    def viewer(self) -> "Viewer":
        if self._viewer is None:
            raise RuntimeError("This ViewerScene is not attached to a Viewer.")
        return self._viewer

    def attach(self, viewer: "Viewer") -> None:
        """Attach the explicit Viewer that owns this runtime scene."""
        self._viewer = viewer

    def _reset_instance_colors(self) -> None:
        """Reset transient picking colors and release cached adapter references."""
        self.instance_colors.clear()
        self._instance_colors_generator = instance_colors_generator()

    def prepare(self) -> None:
        """Create transient render state for every non-root stable object.

        Hidden objects and item-less groups remain part of the runtime
        hierarchy because buffered descendants resolve their parent transforms
        through these entries.

        """
        self._reset_instance_colors()
        for sceneobject in self.objects:
            self.draw_object(sceneobject, context="Viewer", runtime=self)
        for annotation in self.annotations:
            self.draw_annotation(annotation, context="Viewer", runtime=self)

    def render_object(self, sceneobject: SceneObject) -> ViewerSceneObject:
        """Return the transient render state for a stable scene object."""
        try:
            return self.render_objects[sceneobject.guid]
        except KeyError:
            self.draw_object(sceneobject, context="Viewer", runtime=self)
            return self.render_objects[sceneobject.guid]

    def annotation_render_object(self, annotation: SceneAnnotation) -> "WorldAnnotationRenderObject":
        """Return transient render state for one annotation entry.

        Parameters
        ----------
        annotation
            Entry belonging to this scene.

        Returns
        -------
        WorldAnnotationRenderObject
            Existing or newly prepared annotation render helper.

        """
        try:
            return self.annotation_render_objects[annotation.guid]
        except KeyError:
            self.draw_annotation(annotation, context="Viewer", runtime=self)
            return self.annotation_render_objects[annotation.guid]

    def release_picking(self, sceneobject: SceneObject) -> None:
        """Remove transient picking entries for a stable scene object."""
        self.instance_colors = {color: obj for color, obj in self.instance_colors.items() if obj.guid != sceneobject.guid}

    # TODO: These fixed kwargs could be moved to COMPAS core.
    def add(
        self,
        item: Data,
        parent: SceneObject | SceneNode | None = None,
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
    ) -> SceneObject:
        """Add an item to the scene.

        Parameters
        ----------
        item
            Geometry, data structure, scene object, or collection to add.
        parent
            The parent of the item.
        show
            Whether to show object.
            Default to True.
        show_points
            Whether to show points/vertices of the object.
        show_lines
            Whether to show lines/edges of the object.
        show_faces
            Whether to show faces of the object.
        pointcolor
            The color or the dict of colors of the points/vertices of object.
        linecolor
            The color or the dict of colors of the lines/edges of object.
        facecolor
            The color or the dict of colors of the faces of object.
        linewidth
            The line width to be drawn on screen
        pointsize
            The point size to be drawn on screen
        opacity
            The opacity of the object.
        hide_coplanaredges
            Whether to hide the coplanar edges of the mesh.
        use_vertexcolors
            Whether to use vertex color.
        v
            The scene-owned cell count in the V direction. Default is 16.
        u
            The scene-owned cell count in the U direction. Default is 16.
        **kwargs
            Additional options passed to the scene-object constructor.

        Returns
        -------
        SceneObject
            The scene object.

        """
        from compas.datastructures import Graph
        from compas.datastructures import Mesh
        from compas.geometry import Point
        from compas.geometry import Pointcloud

        from .bufferobject import BufferGeometry
        from .collectionobject import Collection

        if isinstance(item, Collection):
            collection_options = dict(kwargs)
            name = collection_options.pop("name", None) or item.name or "Collection"
            transformation = collection_options.pop("transformation", None)
            color = collection_options.get("color")
            group_options = {"show": show, "transformation": transformation}
            if color is not None:
                group_options["color"] = color
            if opacity is not None:
                group_options["opacity"] = opacity
            group = self.add_group(name=name, parent=parent, **group_options)
            for child in item.items:
                self.add(
                    child,
                    parent=group,
                    show=show,
                    show_points=show_points,
                    show_lines=show_lines,
                    show_faces=show_faces,
                    vertexcolor=vertexcolor,
                    pointcolor=pointcolor,
                    linecolor=linecolor,
                    facecolor=facecolor,
                    surfacecolor=surfacecolor,
                    linewidth=linewidth,
                    pointsize=pointsize,
                    opacity=opacity,
                    hide_coplanaredges=hide_coplanaredges,
                    use_vertexcolors=use_vertexcolors,
                    v=v,
                    u=u,
                    **collection_options,
                )
            return group

        edgecolor = kwargs.pop("edgecolor", linecolor)
        if isinstance(item, (Point, Pointcloud)) and show_points is None:
            show_points = True
        if isinstance(item, BufferGeometry):
            show_points = item.points is not None if show_points is None else show_points
            show_lines = item.edges is not None if show_lines is None else show_lines
            show_faces = item.triangles is not None if show_faces is None else show_faces
        options = {"show": show, **kwargs}
        if opacity is not None:
            options["opacity"] = opacity
        if isinstance(item, Mesh):
            options.update(
                {
                    key: value
                    for key, value in {
                        "show_vertices": show_points,
                        "show_edges": show_lines,
                        "show_faces": show_faces,
                        "vertexcolor": vertexcolor or pointcolor,
                        "edgecolor": edgecolor,
                        "facecolor": facecolor,
                        "vertexsize": pointsize,
                        "edgewidth": linewidth,
                        "hide_coplanaredges": hide_coplanaredges,
                        "use_vertexcolors": use_vertexcolors,
                    }.items()
                    if value is not None
                }
            )
        elif isinstance(item, Graph):
            options.update(
                {
                    key: value
                    for key, value in {
                        "show_nodes": show_points,
                        "show_edges": show_lines,
                        "nodecolor": pointcolor,
                        "edgecolor": linecolor,
                        "nodesize": pointsize,
                        "edgewidth": linewidth,
                    }.items()
                    if value is not None
                }
            )
        else:
            options.update(
                {
                    key: value
                    for key, value in {
                        "show_points": show_points,
                        "show_lines": show_lines,
                        "show_surfaces": show_faces,
                        "pointcolor": pointcolor,
                        "linecolor": linecolor,
                        "surfacecolor": surfacecolor or facecolor,
                        "linewidth": linewidth,
                        "pointsize": pointsize,
                        "u": u,
                        "v": v,
                    }.items()
                    if value is not None
                }
            )

        sceneobject = super().add(item=item, parent=parent, **options)

        if self._viewer is not None and self._viewer.running:
            self._viewer.renderer.rebuild_buffers()
            self._viewer.renderer.update()
            self._viewer.ui.sidebar.update()

        return sceneobject

    def add_annotation(
        self,
        item: "TextAnnotation | ArrowAnnotation | DistanceDimension",
        *,
        name: str | None = None,
        show: bool = True,
        style: "DimensionStyle | None" = None,
    ) -> SceneAnnotation:
        """Add a durable annotation outside the spatial hierarchy.

        Parameters
        ----------
        item
            Text, arrow, or distance-dimension annotation data.
        name
            Optional entry name.
        show
            Whether the annotation is visible.
        style
            Distance-dimension presentation style.

        Returns
        -------
        SceneAnnotation
            Added scene annotation entry.

        """
        return super().add_annotation(item, name=name, show=show, style=style)

    def add_annotation_entry(self, entry: SceneAnnotation) -> SceneAnnotation:
        """Attach an annotation entry and refresh only the annotation layer.

        Parameters
        ----------
        entry
            Detached durable annotation entry.

        Returns
        -------
        SceneAnnotation
            The attached entry.

        """
        annotation = super().add_annotation_entry(entry)
        self._refresh_after_annotation_change()
        return annotation

    def remove_annotation(self, entry: SceneAnnotation | UUID) -> None:
        """Remove one annotation entry and its transient render resources.

        Parameters
        ----------
        entry
            Entry or entry GUID to remove.

        """
        annotation = self.annotation(entry) if isinstance(entry, UUID) else entry
        viewer = self._viewer
        if viewer is not None and viewer.running:
            viewer.renderer.makeCurrent()
        try:
            super().remove_annotation(annotation)
        finally:
            if viewer is not None and viewer.running:
                viewer.renderer.doneCurrent()
        self.annotation_render_objects.pop(annotation.guid, None)
        selection_changed = False
        if self._viewer is not None:
            selection_changed = self._viewer.state.annotation_selection.remove(annotation)
        self._refresh_after_annotation_change(selection_changed=selection_changed)

    def _refresh_after_annotation_change(self, *, selection_changed: bool = False) -> None:
        """Prepare and repaint annotations without rebuilding spatial buffers."""
        if self._viewer is None or not self._viewer.running:
            return
        self._viewer.renderer.makeCurrent()
        try:
            for annotation in self.annotations:
                render_object = self.annotation_render_objects.get(annotation.guid)
                if render_object is None:
                    render_object = self.annotation_render_object(annotation)
                if not render_object._inited:
                    render_object.init()
        finally:
            self._viewer.renderer.doneCurrent()
        if not selection_changed:
            self._viewer.ui.sidebar.update()
            self._viewer.renderer.update()

    def remove(self, sceneobject: SceneObject | SceneNode, rebuild_buffers: bool = True) -> None:
        """Remove a scene object from the scene.

        Parameters
        ----------
        sceneobject
            The scene object to remove.
        rebuild_buffers
            Whether to rebuild the buffers.
            Default to True.

        """
        self._remove(sceneobject, rebuild_buffers=rebuild_buffers, cleanup_selection=True)

    def _remove(
        self,
        sceneobject: SceneObject | SceneNode,
        *,
        rebuild_buffers: bool,
        cleanup_selection: bool,
        context_is_current: bool = False,
    ) -> None:
        """Remove one hierarchy with optional deferred selection cleanup."""
        stable_object = self.object(sceneobject) if isinstance(sceneobject, SceneNode) else sceneobject
        removed_objects = [self.object(node) for node in self.node(stable_object.guid).traverse()]
        viewer = self._viewer
        renderer = viewer.renderer if viewer is not None and viewer.running and not context_is_current else None
        if renderer is not None:
            renderer.makeCurrent()
        try:
            super().remove(sceneobject)
        finally:
            if renderer is not None:
                renderer.doneCurrent()
        for removed_object in removed_objects:
            self.render_objects.pop(removed_object.guid, None)
            self.release_picking(removed_object)

        selection_changed = False
        if self._viewer is not None:
            clear_history = getattr(self._viewer, "_clear_transform_history", None)
            if clear_history is not None:
                clear_history()
            if self._viewer.running and rebuild_buffers:
                self._viewer.renderer.rebuild_buffers()
            if cleanup_selection:
                selection_changed = self._viewer.state.selection.remove(*removed_objects)

        if self._viewer is not None and self._viewer.running and rebuild_buffers and not selection_changed:
            self._viewer.renderer.update()
            self._viewer.ui.sidebar.update()

    def clear(
        self,
        clear_scene: bool = True,
        clear_context: bool = True,
        context: str | None = None,
        runtime: object | None = None,
    ) -> None:
        """Clear scene state, runtime buffers, and transient picking colors."""
        viewer = self._viewer
        renderer = viewer.renderer if viewer is not None and viewer.running and (clear_scene or clear_context) else None
        if renderer is not None:
            renderer.makeCurrent()
        try:
            if clear_context:
                super().clear(clear_scene=False, clear_context=True, context=context, runtime=runtime)
            if clear_scene:
                for child in tuple(self.root_node.children):
                    self._remove(child, rebuild_buffers=False, cleanup_selection=False, context_is_current=True)
                for annotation in tuple(self.annotations):
                    super().remove_annotation(annotation)
        finally:
            if renderer is not None:
                renderer.doneCurrent()
        if clear_context:
            self.render_objects.clear()
            self.annotation_render_objects.clear()
        self._reset_instance_colors()

        if clear_scene and self._viewer is not None:
            self._viewer.cancel_measurement()
            clear_history = getattr(self._viewer, "_clear_transform_history", None)
            if clear_history is not None:
                clear_history()
            annotation_selection_changed = self._viewer.state.annotation_selection.clear()
            if self._viewer.running:
                self._viewer.renderer.rebuild_buffers()
            selection_changed = self._viewer.state.selection.clear()
            if not selection_changed and not annotation_selection_changed:
                self._viewer.ui.sidebar.update()
                self._viewer.renderer.update()
