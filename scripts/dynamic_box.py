from random import random

from compas.datastructures import Mesh
from compas.geometry import Box
from compas_viewer import Viewer
from compas.geometry import Translation

viewer = Viewer()

mesh = Mesh.from_shape(Box.from_width_height_depth(2, 2, 2))
obj1 = viewer.scene.add(mesh)
obj2 = viewer.scene.add(mesh, transformation=Translation.from_vector([5, 0, 0]))
obj3 = viewer.scene.add(mesh, transformation=Translation.from_vector([-5, 0, 0]))

obj1.opacity = 0.7

@viewer.on(interval=100)
def deform_mesh(frame):
    obj1.opacity = (frame / 20) % 1
    for v in mesh.vertices():
        vertex: list = mesh.vertex_attributes(v, "xyz")
        vertex[0] += (random() - 0.5) * 0.1
        vertex[1] += (random() - 0.5) * 0.1
        vertex[2] += (random() - 0.5) * 0.1
        mesh.vertex_attributes(v, "xyz", vertex)

    obj1.transformation = Translation.from_vector([random() - 0.5, random() - 0.5, random() - 0.5])
    obj3.transformation *= Translation.from_euler_angles([0.05, 0, 0])

    # Three objects share the same geometry data, but updated differently
    # obj1 should move around and deform
    obj1.update(update_transform=True, update_data=True)

    # obj2 will not move but will deform
    obj2.update(update_transform=False, update_data=True)

    # obj3 will rotate but not deform
    obj3.update(update_transform=True, update_data=False)


viewer.show()
