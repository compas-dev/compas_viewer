from compas.geometry import NurbsCurve
from compas.geometry import Plane
from compas.geometry import Polygon
from compas.geometry import Polyhedron
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()

curve = NurbsCurve.from_points([[0, 0, 0], [1, 1, 0], [2, 0, 0], [3, 1, 0], [4, 0, 0]], degree=3)
viewer.scene.add(curve, name="NURBS curve")

polygon = Polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
viewer.scene.add(polygon, name="Polygon", transformation=Translation.from_vector([0, 3, 0]))

plane = Plane([0, 0, 0], [0, 1, 1])
viewer.scene.add(plane, name="Plane", transformation=Translation.from_vector([3, 3, 0]))

for index, face_count in enumerate((4, 6, 8, 12, 20)):
    polyhedron = Polyhedron.from_platonicsolid(face_count)
    viewer.scene.add(
        polyhedron,
        name=f"{face_count}-face polyhedron",
        transformation=Translation.from_vector([index * 3, 6, 0]),
    )

viewer.show()
