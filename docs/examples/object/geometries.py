import time

from compas.colors import Color
from compas.geometry import (
    Box,
    Capsule,
    Circle,
    Cone,
    Cylinder,
    Ellipse,
    Frame,
    NurbsSurface,
    Plane,
    Point,
    Polyline,
    Sphere,
    Torus,
    Translation,
    Vector,
)
from compas_occ.brep import OCCBrep
from compas_viewer import Viewer

viewer = Viewer(rendermode="lighted", fullscreen=True)

points = [
    [Point(0, 0, 0), Point(1, 0, 0), Point(2, 0, 0), Point(3, 0, 0)],
    [Point(0, 1, 0), Point(1, 1, 2), Point(2, 1, 2), Point(3, 1, 0)],
    [Point(0, 2, 0), Point(1, 2, 2), Point(2, 2, 2), Point(3, 2, 0)],
    [Point(0, 3, 0), Point(1, 3, 0), Point(2, 3, 0), Point(3, 3, 0)],
]
surface = NurbsSurface.from_points(points=points)
obj = viewer.scene.add(
    surface,
    show_points=True,
    show_lines=True,
    pointcolor=Color(0.5, 0.0, 0.0),
    linecolor=Color(0.0, 0.0, 0.5),
)
obj.transformation = Translation.from_vector(Vector(-1.5, -1.5, 0.0))

plane = Plane([0, 0, 0], [0, 0, 1])
obj = viewer.scene.add(plane, size=0.5, linecolor=Color(0.5, 0.0, 0.0), surfacecolor=Color(0.0, 0.0, 0.5))
obj.transformation = Translation.from_vector(Vector(5, 0.0, 0.0))

circle = Circle(0.8, Frame.worldXY())
obj = viewer.scene.add(circle)
obj.transformation = Translation.from_vector(Vector(10, 0.0, 0.0))

ellipse = Ellipse(1.5, 0.5, Frame.worldXY())
obj = viewer.scene.add(
    item=ellipse,
    show_points=True,
    linecolor=Color(1.0, 0.0, 0.0),
    pointcolor=Color(0.0, 0.0, 1.0),
)
obj.transformation = Translation.from_vector(Vector(0, 5, 0))

cone = Cone.from_circle_and_height(circle, 1.5)
obj = viewer.scene.add(cone, surfacecolor=Color(0.5, 0.5, 0.0))
obj.transformation = Translation.from_vector(Vector(5, 5, 0))

box = OCCBrep.from_box(Box(1.5))
cx = OCCBrep.from_cylinder(Cylinder(0.5, 8, frame=Frame.worldYZ()))
cy = OCCBrep.from_cylinder(Cylinder(0.5, 8, frame=Frame.worldZX()))
cz = OCCBrep.from_cylinder(Cylinder(0.5, 8, frame=Frame.worldXY()))
result = box - (cx + cy + cz)
obj = viewer.scene.add(item=result, surfacecolor=Color(0.0, 0.5, 0.5), use_vertexcolors=False)
obj.transformation = Translation.from_vector(Vector(10, 5, 0))

capsule = Capsule(0.8, 1)
obj = viewer.scene.add(item=capsule, surfacecolor=Color(0.0, 0.0, 0.5), show_lines=False)
obj.transformation = Translation.from_vector(Vector(0, 10, 0))

box = Box(1, 1, 1, Frame.worldXY())
obj = viewer.scene.add(
    item=box,
    surfacecolor=Color(0.0, 0.0, 0.5),
    linecolor=Color(0.5, 0.0, 0.0),
    pointcolor=Color(0.0, 0.5, 0.0),
    show_points=True,
)
obj.transformation = Translation.from_vector(Vector(5, 10, 0))

points = [
    [-0.5, -0.5, 0],
    [0.5, -0.5, 0],
    [0.5, 0.5, 0],
    [-0.5, 0.5, 0],
    [-0.5, -0.5, 0],
]
obj = viewer.scene.add(Polyline(points), surfacecolor=Color(0.0, 0.0, 0.5), show_points=True)
obj.transformation = Translation.from_vector(Vector(10, 10, 0))

torus = Torus(radius_axis=1, radius_pipe=0.5)
obj = viewer.scene.add(torus, surfacecolor=Color(0.0, 0.5, 0.0), show_lines=False)
obj.transformation = Translation.from_vector(Vector(0, 15, 0))

sphere = Sphere(frame=Frame.worldXY(), radius=1)
obj = viewer.scene.add(sphere, surfacecolor=Color(0.0, 0.0, 0.5))
obj.transformation = Translation.from_vector(Vector(5, 15, 0))

cylinder = Cylinder(frame=Frame.worldXY(), radius=0.5, height=1)
obj = viewer.scene.add(cylinder, surfacecolor=Color(0.0, 0.5, 0.5))
obj.transformation = Translation.from_vector(Vector(10, 15, 0))

viewer.show()
