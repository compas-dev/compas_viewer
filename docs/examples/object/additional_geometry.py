from compas.geometry import Plane
from compas.geometry import Polygon
from compas.geometry import Polyhedron
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()

polygon = Polygon([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
viewer.scene.add(polygon, name="Polygon")

plane = Plane([0, 0, 0], [0, 1, 1])
viewer.scene.add(plane, name="Plane", transformation=Translation.from_vector([3, 0, 0]))

for index, face_count in enumerate((4, 6, 8, 12, 20)):
    polyhedron = Polyhedron.from_platonicsolid(face_count)
    viewer.scene.add(
        polyhedron,
        name=f"{face_count}-face polyhedron",
        transformation=Translation.from_vector([index * 3, 3, 0]),
    )

viewer.show()
