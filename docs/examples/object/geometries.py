from compas.colors import Color
from compas.geometry import Capsule
from compas.geometry import Circle
from compas.geometry import Cone
from compas.geometry import Ellipse
from compas.geometry import Frame
from compas.geometry import Polygon
from compas.geometry import Polyhedron
from compas.geometry import Translation
from compas.geometry import Vector

from compas_viewer import Viewer

viewer = Viewer()

polygon = Polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0]])
obj = viewer.scene.add(polygon, linescolor=Color(0.0, 0.0, 1.0))

frame = Frame([0, 0, 0], [0, 0, 1])
obj = viewer.scene.add(frame, size=0.5, linescolor=Color(1.0, 0.0, 0.0), facescolor=Color(0.0, 0.0, 1.0))
obj.transformation = Translation.from_vector(Vector(5, 0, 0))

circle = Circle(0.8, frame)
obj = viewer.scene.add(circle, linescolor=Color(0.0, 1.0, 0.0))
obj.transformation = Translation.from_vector(Vector(10, 0, 0))

ellipse = Ellipse(1.5, 0.5, frame)
obj = viewer.scene.add(ellipse, linescolor=Color(1.0, 0.0, 1.0))
obj.transformation = Translation.from_vector(Vector(0, 5, 0))

cone = Cone(circle.radius, 1.5)
obj = viewer.scene.add(cone, facescolor=Color(1.0, 0.0, 0.0))
obj.transformation = Translation.from_vector(Vector(5, 5, 0))

vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 0, 1]]
faces = [[0, 1, 2], [0, 1, 3], [1, 2, 3], [0, 2, 3]]
polyhedron = Polyhedron(vertices, faces)
obj = viewer.scene.add(polyhedron.to_mesh(), facescolor=Color(0.0, 1.0, 0.0))
obj.transformation = Translation.from_vector(Vector(10, 5, 0))

capsule = Capsule(1, 0.3)
obj = viewer.scene.add(capsule, facescolor=Color(0.0, 0.0, 1.0))
obj.transformation = Translation.from_vector(Vector(0, 10, 0))

viewer.show()
