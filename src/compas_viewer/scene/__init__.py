"""
This package provides scene object plugins for visualizing COMPAS objects in `compas_viewer`.
"""

from typing import Union
from compas.scene import register
from compas.plugins import plugin
from compas.datastructures import Mesh
from compas.datastructures import Graph
from compas.geometry import (
    Point,
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
    Frame,
    NurbsSurface,
    Geometry,
)

from .sceneobject import ViewerSceneObject
from .meshobject import MeshObject
from .graphobject import GraphObject
from .pointobject import PointObject
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
from .nurbssurfaceobject import NurbsSurfaceObject
from .collectionobject import CollectionObject
from .geometryobject import GeometryObject


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
    register(list[Union[Geometry, Mesh]], CollectionObject, context="Viewer")

    try:
        from compas_occ.brep import OCCBrep
        from .brepobject import BRepObject

        register(OCCBrep, BRepObject, context="Viewer")
        register(NurbsSurface, NurbsSurfaceObject, context="Viewer")

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
]
