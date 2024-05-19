from random import random

from compas.geometry import Box
from compas.datastructures import Mesh
from compas_viewer import Viewer

viewer = Viewer()

mesh = Mesh.from_shape(Box.from_width_height_depth(2, 2, 2))
obj = viewer.scene.add(mesh)

@viewer.on(interval=100)
def deform_mesh(frame):
    for v in mesh.vertices():
        vertex: list = mesh.vertex_attributes(v, "xyz") 
        vertex[0] += (random() - 0.5) * 0.1
        vertex[1] += (random() - 0.5) * 0.1
        vertex[2] += (random() - 0.5) * 0.1
        mesh.vertex_attributes(v, "xyz", vertex)
    obj.init() # TODO: this should called, fix later
    obj.update()
    print(frame)


viewer.show()
