from random import Random

import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas_viewer import Viewer

viewer = Viewer()
rng = Random(42)

mesh = Mesh.from_off(compas.get("tubemesh.off"))
sceneobject = viewer.scene.add(mesh, facecolor=Color.cyan(), use_vertexcolors=False)


@viewer.on(interval=200)
def deform_mesh(frame: int) -> None:
    for vertex in mesh.vertices():
        point = mesh.vertex_point(vertex)
        point[0] += rng.random() - 0.5
        point[1] += rng.random() - 0.5
        point[2] += rng.random() - 0.5
        mesh.set_vertex_point(vertex, point)
    viewer.refresh_geometry((sceneobject,))
    print(frame)


viewer.show()
