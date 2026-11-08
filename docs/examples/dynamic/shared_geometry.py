from random import Random

from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()
rng = Random(42)

mesh = Box(2, 2, 2).to_polygonal_surface().to_mesh()
moving_object = viewer.scene.add(mesh)
static_object = viewer.scene.add(mesh, transformation=Translation.from_vector([5, 0, 0]))
rotating_object = viewer.scene.add(mesh, transformation=Translation.from_vector([-5, 0, 0]))

moving_object.opacity = 0.7


@viewer.on(interval=100)
def deform_mesh(frame: int) -> None:
    moving_object.opacity = (frame / 20) % 1
    for vertex in mesh.vertices():
        point = mesh.vertex_point(vertex)
        point[0] += (rng.random() - 0.5) * 0.1
        point[1] += (rng.random() - 0.5) * 0.1
        point[2] += (rng.random() - 0.5) * 0.1
        mesh.set_vertex_point(vertex, point)

    moving_object.transformation = Translation.from_vector([rng.random() - 0.5, rng.random() - 0.5, rng.random() - 0.5])
    rotating_object.transformation *= Translation.from_euler_angles([0.05, 0, 0])

    # All three scene objects share the modified mesh, so regenerate their
    # geometry. Then synchronize the two externally assigned transformations.
    viewer.refresh_geometry()
    viewer.refresh_transform((moving_object, rotating_object))


viewer.show()
