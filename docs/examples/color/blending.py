from random import random

import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Scale
from compas.geometry import Translation

from compas_viewer import Viewer

viewer = Viewer()

mesh = Mesh.from_obj(compas.get("faces.obj"))
T = Translation.from_vector([0, 0, 1])
S = Scale.from_factors([0.5, 0.5, 0.5])
mesh.transform(T * S)

mesh2 = mesh.transformed(Translation.from_vector([-6, 0, 0]))

facescolor = {k: Color(random(), random(), random()) for k in mesh.faces()}
linescolor = {k: Color(random(), random(), random()) for k in mesh.edges()}
pointscolor = {k: Color(random(), random(), random()) for k in mesh.vertices()}

viewer.scene.add(mesh, name="mesh1", show_points=True, facescolor=facescolor, linescolor=linescolor, pointscolor=pointscolor)  # type: ignore
viewer.scene.add(
    mesh2,
    name="mesh2",
    show_points=True,
    facescolor=Color.red(),
    linescolor=Color.green(),
    pointscolor=Color.blue(),
)

viewer.show()
