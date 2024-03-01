from random import random

import compas
from compas.colors import Color
from compas.datastructures import Mesh

from compas_viewer import Viewer

viewer = Viewer()

mesh = Mesh.from_obj(compas.get("faces.obj"))

for vertex in mesh.vertices():
    mesh.vertex_attribute(vertex, "color", Color.from_i(random()))

viewer.scene.add(mesh, use_vertexcolors=True)

viewer.show()
