from compas.datastructures import Mesh
from compas.geometry import Box, Sphere


from compas_viewer import Viewer


viewer = Viewer()

# mesh = Mesh.from_obj(compas.get("tubemesh.obj"))
# mesh = Mesh.from_polyhedron(12)
# mesh  = Mesh.from_shape(Box.from_width_height_depth(1, 1, 1))
mesh = Mesh.from_shape(Sphere(3))
viewer.add(mesh)

viewer.show()
