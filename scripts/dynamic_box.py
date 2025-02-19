from random import random

from compas.datastructures import Mesh
from compas.geometry import Box
from compas_viewer import Viewer
from compas.geometry import Translation, Scale

viewer = Viewer()

mesh = Mesh.from_shape(Box.from_width_height_depth(2, 2, 2))
obj1 = viewer.scene.add(mesh)
obj2 = viewer.scene.add(mesh)
obj2.transformation = Translation.from_vector([5, 0, 0])

obj3 = viewer.scene.add(mesh)
obj3.transformation = Translation.from_vector([-5, 0, 0])

@viewer.on(interval=100)
def deform_mesh(frame):
    for v in mesh.vertices():
        vertex: list = mesh.vertex_attributes(v, "xyz")
        vertex[0] += (random() - 0.5) * 0.1
        vertex[1] += (random() - 0.5) * 0.1
        vertex[2] += (random() - 0.5) * 0.1
        mesh.vertex_attributes(v, "xyz", vertex)

    obj1.update()
    obj2.update()

    obj1.transformation = Translation.from_vector([random() - 0.5, random() - 0.5, random() - 0.5])
    # obj1.transformation = Scale.from_factors([0.51, 0.51, 0.51])
    obj3.transformation *= Translation.from_euler_angles([0.05, 0, 0])

    viewer.renderer.buffer_manager.update_object_transform(obj1)
    viewer.renderer.buffer_manager.update_object_data(obj1)
    viewer.renderer.buffer_manager.update_object_data(obj2)
    viewer.renderer.buffer_manager.update_object_transform(obj3)
    # viewer.renderer.buffer_manager.update_object_settings(obj1, True)

# TODO: clean up all the update calls

viewer.show()
