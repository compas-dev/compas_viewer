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
from .boxobject import BoxObject
from .torusobject import TorusObject
from .polylineobject import PolylineObject
from .polygonobject import PolygonObject
from .sphereobject import SphereObject
from .planeobject import PlaneObject
from .cylinderobject import CylinderObject
from .ellipseobject import EllipseObject
from .coneobject import ConeObject
from .capsuleobject import CapsuleObject
from .polyhedronobject import PolyhedronObject
from .geometryobject import GeometryObject
from .groupobject import Group
from .groupobject import GroupObject
from .collectionobject import Collection
from .collectionobject import CollectionObject

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
    register(Box, BoxObject, context="Viewer")
    register(Polyline, PolylineObject, context="Viewer")
    register(Torus, TorusObject, context="Viewer")
    register(Polygon, PolygonObject, context="Viewer")
    register(Sphere, SphereObject, context="Viewer")
    register(Plane, PlaneObject, context="Viewer")
    register(Cylinder, CylinderObject, context="Viewer")
    register(Ellipse, EllipseObject, context="Viewer")
    register(Cone, ConeObject, context="Viewer")
    register(Capsule, CapsuleObject, context="Viewer")
    register(Polyhedron, PolyhedronObject, context="Viewer")
    register(list, GroupObject, context="Viewer")
    register(Collection, CollectionObject, context="Viewer")

    try:
        from compas_occ.brep import OCCBrep
        from .brepobject import BRepObject
        from .nurbssurfaceobject import NurbsSurfaceObject
        from compas.geometry import NurbsCurve
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
    "BoxObject",
    "Torus",
    "TorusObject",
    "Polygon",
    "PolygonObject",
    "Sphere",
    "SphereObject",
    "Plane",
    "PlaneObject",
    "Cylinder",
    "CylinderObject",
    "Ellipse",
    "EllipseObject",
    "Cone",
    "ConeObject",
    "Capsule",
    "CapsuleObject",
    "NurbsSurface",
    "NurbsSurfaceObject",
    "GeometryObject",
    "Group",
    "GroupObject",
    "Collection",
    "CollectionObject",
    "ViewerScene",
]
