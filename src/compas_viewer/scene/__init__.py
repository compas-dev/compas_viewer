"""
This package provides scene object plugins for visualizing COMPAS objects in `compas_viewer`.
"""

from compas.scene import register
from compas.plugins import plugin
from compas.datastructures import Mesh
from compas.datastructures import Graph
from compas.geometry import (
    Point,
    Pointcloud,
    Line,
    Vector,
    Circle,
    Box,
    Polyline,
    Torus,
    Polygon,
    Sphere,
    Plane,
    Cylinder,
    Ellipse,
    Cone,
    Capsule,
    Polyhedron,
    Frame,
    NurbsSurface,
)

from .sceneobject import ViewerSceneObject
from .meshobject import MeshObject
from .graphobject import GraphObject
from .pointobject import PointObject
from .pointcloudobject import PointcloudObject
from .lineobject import LineObject
from .vectorobject import VectorObject
from .tagobject import TagObject, Tag
from .frameobject import FrameObject
from .circleobject import CircleObject
from .polylineobject import PolylineObject
from .polygonobject import PolygonObject
from .planeobject import PlaneObject
from .ellipseobject import EllipseObject
from .polyhedronobject import PolyhedronObject
from .geometryobject import GeometryObject
from .shapeobject import ShapeObject
from .group import Group
from .collectionobject import Collection
from .collectionobject import CollectionObject
from .bufferobject import BufferGeometry
from .bufferobject import BufferObject
from .scene import ViewerScene


@plugin(category="drawing-utils", requires=["compas_viewer"])
def clear(guids: list[str]):
    for obj in guids:
        del obj


@plugin(category="drawing-utils", requires=["compas_viewer"])
def redraw():
    pass


@plugin(category="factories", requires=["compas_viewer"])
def register_scene_objects():
    register(Mesh, MeshObject, context="Viewer")
    register(Graph, GraphObject, context="Viewer")
    register(Point, PointObject, context="Viewer")
    register(Pointcloud, PointcloudObject, context="Viewer")
    register(Line, LineObject, context="Viewer")
    register(Tag, TagObject, context="Viewer")
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
    register(Collection, CollectionObject, context="Viewer")
    register(BufferGeometry, BufferObject, context="Viewer")

    try:
        from compas.geometry import NurbsCurve
        from compas_occ.brep import OCCBrep

        from .brepobject import BRepObject
        from .nurbssurfaceobject import NurbsSurfaceObject
        from .nurbscurveobject import NurbsCurveObject

        register(OCCBrep, BRepObject, context="Viewer")
        register(NurbsSurface, NurbsSurfaceObject, context="Viewer")
        register(NurbsCurve, NurbsCurveObject, context="Viewer")

    except ImportError:
        pass


__all__ = [
    "ViewerSceneObject",
    "Mesh",
    "MeshObject",
    "Point",
    "PointObject",
    "Line",
    "LineObject",
    "Tag",
    "TagObject",
    "Frame",
    "FrameObject",
    "Vector",
    "VectorObject",
    "Circle",
    "CircleObject",
    "Polyline",
    "PolylineObject",
    "Box",
    "Torus",
    "Polygon",
    "PolygonObject",
    "Sphere",
    "Plane",
    "PlaneObject",
    "Cylinder",
    "Ellipse",
    "EllipseObject",
    "Cone",
    "Capsule",
    "NurbsSurface",
    "NurbsSurfaceObject",
    "GeometryObject",
    "ShapeObject",
    "Group",
    "Collection",
    "CollectionObject",
    "BufferGeometry",
    "BufferObject",
    "ViewerScene",
]
