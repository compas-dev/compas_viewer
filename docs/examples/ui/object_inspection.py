from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Sphere
from compas.geometry import Translation
from compas_viewer import Viewer

vertices = [
    [0.0, 0.0, 0.0],
    [2.0, 0.0, 0.0],
    [2.0, 2.0, 0.0],
    [0.0, 2.0, 0.0],
]
faces = [[0, 1, 2, 3]]

mesh = Mesh.from_vertices_and_faces(vertices, faces)
mesh.update_default_vertex_attributes({"temperature": 20.0})
mesh.update_default_edge_attributes({"load": 0.0})
mesh.update_default_face_attributes({"thickness": 0.1})
mesh.vertex_attribute(2, "temperature", 45.0)
mesh.edge_attribute((0, 1), "load", 12.5)
mesh.face_attribute(0, "thickness", 0.25)

viewer = Viewer()
viewer.sidebar_items.insert(2, {"type": "DatastructureAttributes"})
viewer.scene.add(
    Sphere(1.0),
    name="Editable sphere",
    surfacecolor=Color(0.2, 0.6, 0.9),
    opacity=0.8,
)
viewer.scene.add(
    mesh,
    name="Mesh attributes",
    transformation=Translation.from_vector([3.0, -1.0, 0.0]),
)
viewer.show()
