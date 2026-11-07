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

from .parameters import ObjectParameter, inspect_object_parameters, modify_object_parameters, object_parameter_values
from .arrowoverlayobject import ArrowOverlay
from .tagobject import Tag, TextAnnotation
from .group import Group
from .collectionobject import Collection
from .bufferobject import BufferGeometry
from .scene import ViewerScene


__all__ = [
    "ArrowOverlay",
    "ObjectParameter",
    "Mesh",
    "Graph",
    "Point",
    "Pointcloud",
    "Line",
    "Tag",
    "TextAnnotation",
    "Frame",
    "Vector",
    "Circle",
    "Polyline",
    "Box",
    "Torus",
    "Polygon",
    "Sphere",
    "Plane",
    "Cylinder",
    "Ellipse",
    "Cone",
    "Capsule",
    "Polyhedron",
    "Brep",
    "NurbsCurve",
    "NurbsSurface",
    "PolygonalSurface",
    "Surface",
    "Group",
    "Collection",
    "BufferGeometry",
    "ViewerScene",
    "inspect_object_parameters",
    "modify_object_parameters",
    "object_parameter_values",
]
