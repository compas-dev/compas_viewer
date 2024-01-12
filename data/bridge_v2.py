from compas import json_load
from compas.colors import Color
from compas.geometry import Vector

from compas_viewer import Viewer

meshes = json_load(r"data\viewobjects.json")

param = 0.8


viewer = Viewer(rendermode="shaded")

for i, mesh in enumerate(meshes):
    viewer.add(mesh, use_vertexcolors=False, show_lines=True, show_points=False)

    for face in mesh.faces():
        vector = Vector(*mesh.face_normal(face))
        vector.unitize()

        if vector.dot(Vector.Zaxis()) > param:
            color_param = (abs(vector.dot(Vector.Zaxis())) - param) * (1 / (1 - param))

            viewer.add(
                vector * 0.1,
                anchor=mesh.face_center(face),
                linescolor=Color.from_i(color_param),
            )

viewer.objects[1091].is_selected = True

viewer.show()
