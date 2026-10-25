"""COMPAS plugin implementations provided by :mod:`compas_viewer`."""

import sys

from compas.plugins import plugin


@plugin(category="drawing-utils")
def clear(guids: list[object] | None = None) -> None:
    """Clear viewer objects.

    Parameters
    ----------
    guids
        The identifiers to clear. The viewer manages clearing through its scene,
        so this hook currently has no additional work to perform.

    """


@plugin(category="drawing-utils")
def before_draw() -> None:
    """Prepare the viewer before drawing a scene."""


@plugin(category="drawing-utils")
def after_draw(drawn_objects: list[object]) -> None:
    """Complete viewer drawing operations.

    Parameters
    ----------
    drawn_objects
        The objects drawn by the active scene.

    """


@plugin(category="factories")
def register_scene_objects() -> None:
    """Register the scene object implementations provided by the viewer."""
    from compas.datastructures import Graph
    from compas.datastructures import Mesh
    from compas.geometry import Box
    from compas.geometry import Brep
    from compas.geometry import Capsule
    from compas.geometry import Circle
    from compas.geometry import Cone
    from compas.geometry import Cylinder
    from compas.geometry import Ellipse
    from compas.geometry import Frame
    from compas.geometry import Line
    from compas.geometry import NurbsCurve
    from compas.geometry import NurbsSurface
    from compas.geometry import Plane
    from compas.geometry import Point
    from compas.geometry import Pointcloud
    from compas.geometry import Polygon
    from compas.geometry import PolygonalSurface
    from compas.geometry import Polyhedron
    from compas.geometry import Polyline
    from compas.geometry import Sphere
    from compas.geometry import Surface
    from compas.geometry import Torus
    from compas.geometry import Vector
    from compas.scene import register
    from compas_viewer.scene import ArrowOverlay
    from compas_viewer.scene import ArrowOverlayObject
    from compas_viewer.scene import BRepObject
    from compas_viewer.scene import BufferGeometry
    from compas_viewer.scene import BufferObject
    from compas_viewer.scene import CircleObject
    from compas_viewer.scene import Collection
    from compas_viewer.scene import CollectionObject
    from compas_viewer.scene import EllipseObject
    from compas_viewer.scene import FrameObject
    from compas_viewer.scene import GraphObject
    from compas_viewer.scene import LineObject
    from compas_viewer.scene import MeshObject
    from compas_viewer.scene import NurbsCurveObject
    from compas_viewer.scene import PlaneObject
    from compas_viewer.scene import PointcloudObject
    from compas_viewer.scene import PointObject
    from compas_viewer.scene import PolygonalSurfaceObject
    from compas_viewer.scene import PolygonObject
    from compas_viewer.scene import PolyhedronObject
    from compas_viewer.scene import PolylineObject
    from compas_viewer.scene import ShapeObject
    from compas_viewer.scene import SurfaceObject
    from compas_viewer.scene import Tag
    from compas_viewer.scene import TagObject
    from compas_viewer.scene import VectorObject

    register(Mesh, MeshObject, context="Viewer")
    register(Graph, GraphObject, context="Viewer")
    register(Point, PointObject, context="Viewer")
    register(Pointcloud, PointcloudObject, context="Viewer")
    register(Line, LineObject, context="Viewer")
    register(Tag, TagObject, context="Viewer")
    register(ArrowOverlay, ArrowOverlayObject, context="Viewer")
    register(Frame, FrameObject, context="Viewer")
    register(Vector, VectorObject, context="Viewer")
    register(Circle, CircleObject, context="Viewer")
    register(Box, ShapeObject, context="Viewer")
    register(Polyline, PolylineObject, context="Viewer")
    register(Torus, ShapeObject, context="Viewer")
    register(Polygon, PolygonObject, context="Viewer")
    register(Sphere, ShapeObject, context="Viewer")
    register(Plane, PlaneObject, context="Viewer")
    register(Cylinder, ShapeObject, context="Viewer")
    register(Ellipse, EllipseObject, context="Viewer")
    register(Cone, ShapeObject, context="Viewer")
    register(Capsule, ShapeObject, context="Viewer")
    register(Polyhedron, PolyhedronObject, context="Viewer")
    register(PolygonalSurface, PolygonalSurfaceObject, context="Viewer")
    register(Surface, SurfaceObject, context="Viewer")
    register(Collection, CollectionObject, context="Viewer")
    register(BufferGeometry, BufferObject, context="Viewer")
    register(Brep, BRepObject, context="Viewer")
    register(NurbsSurface, SurfaceObject, context="Viewer")
    register(NurbsCurve, NurbsCurveObject, context="Viewer")


def ensure_scene_objects_registered() -> None:
    """Ensure the viewer plugin is loaded and its scene objects are registered.

    COMPAS only invokes its scene-registration pluggable automatically while
    the complete scene-object registry is empty. This explicit startup hook
    also covers processes where context-independent registrations already made
    that registry truthy, and source checkouts without installed entry-point
    metadata.

    """
    from compas.datastructures import Mesh
    from compas.geometry import Point
    from compas.geometry import Sphere
    from compas.geometry import Surface
    from compas.plugins import plugin_manager
    from compas.scene import register_scene_objects as register_all_scene_objects
    from compas.scene.context import ITEM_SCENEOBJECT
    from compas_viewer.scene import MeshObject
    from compas_viewer.scene import PointObject
    from compas_viewer.scene import ShapeObject
    from compas_viewer.scene import SurfaceObject

    expected = {
        Mesh: MeshObject,
        Point: PointObject,
        Sphere: ShapeObject,
        Surface: SurfaceObject,
    }
    registry = ITEM_SCENEOBJECT["Viewer"]
    if all(registry.get(item_type) is sceneobject_type for item_type, sceneobject_type in expected.items()):
        return

    plugin_manager.register_module(sys.modules[__name__])
    register_all_scene_objects()


__all__ = ["after_draw", "before_draw", "clear", "ensure_scene_objects_registered", "register_scene_objects"]
