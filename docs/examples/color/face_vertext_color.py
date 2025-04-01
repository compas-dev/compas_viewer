from random import random

import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas_viewer import Viewer

viewer = Viewer()

mesh = Mesh.from_obj(compas.get("faces.obj"))

vertexcolor = {vertex: Color.from_i(random()) for vertex in mesh.vertices()}

viewer.scene.add(mesh, use_vertexcolors=True, vertexcolor=vertexcolor)

viewer.show()
