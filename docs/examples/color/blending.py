from random import Random

import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Scale
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()
rng = Random(42)

mesh = Mesh.from_obj(compas.get("faces.obj"))
translation = Translation.from_vector([0, 0, 1])
scale = Scale.from_factors([0.5, 0.5, 0.5])
mesh.transform(translation * scale)

mesh2 = mesh.transformed(Translation.from_vector([-6, 0, 0]))

facecolor = {face: Color(rng.random(), rng.random(), rng.random()) for face in mesh.faces()}
edgecolor = {edge: Color(rng.random(), rng.random(), rng.random()) for edge in mesh.edges()}
vertexcolor = {vertex: Color(rng.random(), rng.random(), rng.random()) for vertex in mesh.vertices()}

viewer.scene.add(mesh, name="mesh1", show_points=True, facecolor=facecolor, edgecolor=edgecolor, vertexcolor=vertexcolor, use_vertexcolors=True)
viewer.scene.add(
    mesh2,
    name="mesh2",
    show_points=True,
    facecolor=Color.red(),
    edgecolor=Color.green(),
    vertexcolor=Color.blue(),
)

viewer.show()
