"""
This package provides scene object plugins for visualizing COMPAS objects in `compas_viewer`.
"""
from matplotlib.patches import Polygon
from compas.scene import register
from compas.plugins import plugin
from .sceneobject import ViewerSceneObject
from compas.datastructures import Mesh, Network
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
)


from .meshobject import MeshObject

from .pointobject import PointObject
from .lineobject import LineObject
from .vectorobject import VectorObject
from .tagobject import TagObject, Tag
from .gridobject import GridObject, Grid
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
from .frameobject import FrameObject


@plugin(category="drawing-utils", requires=["compas_viewer"])
def clear(guids=None):
    pass


@plugin(category="drawing-utils", requires=["compas_viewer"])
def redraw():
    pass


@plugin(category="factories", requires=["compas_viewer"])
def register_scene_objects():
    register(Mesh, MeshObject, context="Viewer")
    register(Point, PointObject, context="Viewer")
    register(Line, LineObject, context="Viewer")
    register(Tag, TagObject, context="Viewer")
    register(Grid, GridObject, context="Viewer")
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
    register(Frame, FrameObject, context="Viewer")
    try:
        from compas_occ.brep import BRep
        from .brepobject import BRepObject

        register(BRep, BRepObject, context="Viewer")
    except:
        pass


__all__ = [
    "ViewerSceneObject",
    "MeshObject",
    "PointObject",
    "LineObject",
    "TagObject",
    "Tag",
    "GridObject",
    "Grid",
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
    "Frame",
    "FrameObject",
]
