"""Transient Viewer rendering state for stable scene objects."""

from typing import TYPE_CHECKING

from compas.scene import SceneObject

if TYPE_CHECKING:
    from compas.scene import Scene

    from .sceneobject import ViewerSceneObject


def create_render_object(sceneobject: SceneObject, runtime: object) -> "ViewerSceneObject":
    """Create the transient render helper for a stable scene object."""
    from compas.datastructures import Graph
    from compas.datastructures import Mesh
    from compas.geometry import Brep
    from compas.geometry import Circle
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
    from compas.geometry import Shape
    from compas.geometry import Surface
    from compas.geometry import Vector
    from compas.scene import ArrowAnnotation
    from compas.scene import DistanceDimension
    from compas.scene import TextAnnotation

    from .annotationobject import ArrowAnnotationRenderObject
    from .annotationobject import DistanceDimensionRenderObject
    from .annotationobject import TextAnnotationRenderObject
    from .brepobject import BRepObject
    from .bufferobject import BufferGeometry
    from .bufferobject import BufferObject
    from .circleobject import CircleObject
    from .ellipseobject import EllipseObject
    from .frameobject import FrameObject
    from .graphobject import GraphObject
    from .lineobject import LineObject
    from .meshobject import MeshObject
    from .nurbscurveobject import NurbsCurveObject
    from .planeobject import PlaneObject
    from .pointcloudobject import PointcloudObject
    from .pointobject import PointObject
    from .polygonalsurfaceobject import PolygonalSurfaceObject
    from .polygonobject import PolygonObject
    from .polyhedronobject import PolyhedronObject
    from .polylineobject import PolylineObject
    from .sceneobject import ViewerSceneObject
    from .shapeobject import ShapeObject
    from .surfaceobject import SurfaceObject
    from .vectorobject import VectorObject

    item = sceneobject.item
    pairs = (
        (TextAnnotation, TextAnnotationRenderObject),
        (ArrowAnnotation, ArrowAnnotationRenderObject),
        (DistanceDimension, DistanceDimensionRenderObject),
        (BufferGeometry, BufferObject),
        (Mesh, MeshObject),
        (Graph, GraphObject),
        (Frame, FrameObject),
        (Vector, VectorObject),
        (Point, PointObject),
        (Pointcloud, PointcloudObject),
        (Line, LineObject),
        (Circle, CircleObject),
        (Ellipse, EllipseObject),
        (Plane, PlaneObject),
        (Polyline, PolylineObject),
        (Polygon, PolygonObject),
        (Polyhedron, PolyhedronObject),
        (PolygonalSurface, PolygonalSurfaceObject),
        (Brep, BRepObject),
        (NurbsCurve, NurbsCurveObject),
        (NurbsSurface, SurfaceObject),
        (Surface, SurfaceObject),
        (Shape, ShapeObject),
    )
    for item_type, render_type in pairs:
        if isinstance(item, item_type):
            return render_type(sceneobject=sceneobject, runtime=runtime)
    render_object = ViewerSceneObject(sceneobject=sceneobject, runtime=runtime)
    object.__setattr__(render_object, "show_points", False)
    object.__setattr__(render_object, "show_lines", False)
    object.__setattr__(render_object, "show_surfaces", False)
    object.__setattr__(render_object, "pointsize", 1.0)
    object.__setattr__(render_object, "linewidth", 1.0)
    return render_object


def draw(scene: "Scene", sceneobject: SceneObject, runtime: object | None) -> list[object]:
    """Prepare one stable scene object in a Viewer runtime."""
    from .scene import ViewerScene

    viewer_scene = getattr(runtime, "scene", runtime)
    if not isinstance(viewer_scene, ViewerScene):
        raise TypeError("Viewer draw operations require a Viewer or ViewerScene runtime.")
    render_object = create_render_object(sceneobject, runtime or viewer_scene)
    viewer_scene.render_objects[sceneobject.guid] = render_object
    return []


def clear(scene: "Scene", sceneobject: SceneObject, runtime: object | None, resources: tuple[object, ...]) -> None:
    """Release one stable scene object's transient Viewer state."""
    from .scene import ViewerScene

    viewer_scene = getattr(runtime, "scene", runtime)
    if not isinstance(viewer_scene, ViewerScene):
        return
    render_object = viewer_scene.render_objects.pop(sceneobject.guid, None)
    clear_method = getattr(type(render_object), "clear", None) if render_object is not None else None
    if clear_method is not None:
        clear_method(render_object)
    viewer_scene.release_picking(sceneobject)
