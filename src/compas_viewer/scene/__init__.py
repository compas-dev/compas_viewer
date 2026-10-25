"""
This package provides scene object plugins for visualizing COMPAS objects in `compas_viewer`.
"""

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
    Brep,
    NurbsCurve,
    NurbsSurface,
    PolygonalSurface,
    Surface,
)

from .sceneobject import ViewerSceneObject
from .parameters import ObjectParameter, inspect_object_parameters, modify_object_parameters, object_parameter_values
from .arrowoverlayobject import ArrowOverlay, ArrowOverlayObject
from .meshobject import MeshObject
from .graphobject import GraphObject
from .pointobject import PointObject
from .pointcloudobject import PointcloudObject
from .lineobject import LineObject
from .vectorobject import VectorObject
from .tagobject import Tag, TagObject, TextAnnotation
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
from .brepobject import BRepObject
from .nurbscurveobject import NurbsCurveObject
from .nurbssurfaceobject import NurbsSurfaceObject
from .polygonalsurfaceobject import PolygonalSurfaceObject
from .surfaceobject import SurfaceObject
from .tessellationobject import TessellationObject


__all__ = [
    "ArrowOverlay",
    "ArrowOverlayObject",
    "ObjectParameter",
    "ViewerSceneObject",
    "Mesh",
    "MeshObject",
    "Graph",
    "GraphObject",
    "Point",
    "PointObject",
    "Pointcloud",
    "PointcloudObject",
    "Line",
    "LineObject",
    "Tag",
    "TagObject",
    "TextAnnotation",
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
    "Polyhedron",
    "PolyhedronObject",
    "Brep",
    "BRepObject",
    "NurbsCurve",
    "NurbsCurveObject",
    "NurbsSurface",
    "NurbsSurfaceObject",
    "PolygonalSurface",
    "PolygonalSurfaceObject",
    "Surface",
    "SurfaceObject",
    "TessellationObject",
    "GeometryObject",
    "ShapeObject",
    "Group",
    "Collection",
    "CollectionObject",
    "BufferGeometry",
    "BufferObject",
    "ViewerScene",
    "inspect_object_parameters",
    "modify_object_parameters",
    "object_parameter_values",
]
