from compas.colors import Color
from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.geometry import Sphere
from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.uidefinitions import default_sidebar_items

vertices = [
    [0.0, 0.0, 0.0],
    [2.0, 0.0, 0.0],
    [2.0, 2.0, 0.0],
    [0.0, 2.0, 0.0],
]
faces = [[0, 1, 2, 3]]

mesh = Mesh.from_vertices_and_faces(vertices, faces)
mesh.attributes["discipline"] = "Structures"
mesh.attributes["revision"] = 3
mesh.update_default_vertex_attributes({"temperature": 20.0})
mesh.update_default_edge_attributes({"load": 0.0})
mesh.update_default_face_attributes({"thickness": 0.1})
mesh.vertex_attribute(2, "temperature", 45.0)
mesh.edge_attribute((0, 1), "load", 12.5)
mesh.face_attribute(0, "thickness", 0.25)

graph = Graph(name="Load path")
graph.attributes["discipline"] = "Structures"
graph.update_default_node_attributes({"support": False})
graph.update_default_edge_attributes({"force": 0.0})
graph.add_node("A", x=0.0, y=0.0, z=0.0, support=True)
graph.add_node("B", x=2.0, y=0.0, z=1.0)
graph.add_edge("A", "B", force=18.0)

sidebar_items = default_sidebar_items()
sidebar_items.insert(2, {"type": "DatastructureAttributes"})
viewer = Viewer(sidebar_items=sidebar_items)
viewer.scene.add(
    Sphere(1.0),
    name="Editable sphere",
    surfacecolor=Color(0.2, 0.6, 0.9),
    opacity=0.8,
)
viewer.scene.add(
    mesh,
    name="Mesh placement A",
    transformation=Translation.from_vector([3.0, -1.0, 0.0]),
)
viewer.scene.add(
    mesh,
    name="Mesh placement B",
    transformation=Translation.from_vector([3.0, 2.0, 0.0]),
)
viewer.scene.add(
    graph,
    name="Graph attributes",
    transformation=Translation.from_vector([0.0, 3.0, 0.0]),
)
viewer.show()
