from random import random

import compas
from compas.colors import Color
from compas.datastructures import Mesh

from compas_viewer import Viewer

viewer = Viewer()

mesh = Mesh.from_off(compas.get("tubemesh.off"))
obj = viewer.scene.add(mesh, surfacecolor=Color.cyan(), use_vertexcolors=False)


@viewer.on(interval=1000)
def deform_mesh(frame):
    for v in mesh.vertices():
        vertex: list = mesh.vertex_attributes(v, "xyz")  # type: ignore
        vertex[0] += random() - 0.5
        vertex[1] += random() - 0.5
        vertex[2] += random() - 0.5
        mesh.vertex_attributes(v, "xyz", vertex)
    obj.init() # ???
    obj.update()
    print(frame)

viewer.renderer.camera.zoom_extents()
viewer.show()
