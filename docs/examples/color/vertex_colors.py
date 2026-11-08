from random import Random

import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas_viewer import Viewer

viewer = Viewer()
rng = Random(42)

mesh = Mesh.from_obj(compas.get("faces.obj"))

vertexcolor = {vertex: Color.from_i(rng.random()) for vertex in mesh.vertices()}

viewer.scene.add(mesh, use_vertexcolors=True, vertexcolor=vertexcolor)

viewer.show()
