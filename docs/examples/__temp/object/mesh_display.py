import compas
from compas.datastructures import Mesh
from compas.geometry import Scale
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()

mesh = Mesh.from_obj(compas.get("faces.obj"))
T = Translation.from_vector([0, 0, 1])
S = Scale.from_factors([0.5, 0.5, 0.5])
mesh.transform(T * S)

mesh2 = mesh.transformed(Translation.from_vector([-6, 0, 0]))

viewer.scene.add(mesh, hide_coplanaredges=False, use_vertexcolors=False)
viewer.scene.add(mesh2, hide_coplanaredges=True, use_vertexcolors=False)

viewer.show()
