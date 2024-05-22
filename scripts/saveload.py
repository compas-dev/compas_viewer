import compas
from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer
from compas.data import json_dump
from compas.data import json_load
from compas.scene import Scene

# Save and load a scene
viewer = Viewer()
mesh = Mesh.from_off(compas.get("tubemesh.off"))
obj = viewer.scene.add(mesh, show_points=True, facecolor=Color.blue(), linecolor=Color.red(), pointcolor=Color.green())
for i in range(5):
    for j in range(5):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            show_points=True,
            linecolor=Color.white(),
            pointcolor=Color.black(),
            pointsize=10,
            facecolor=Color(i / 10, j / 10, 0.0),
            name=f"Box_{i}_{j}",
        )

json_dump(viewer.scene, "temp/scene1.json")
viewer.show()


viewer.scene = json_load("temp/scene1.json")
viewer.show()



# Viewer with a generic scene
# Note the generic scene can be more limited in visualization options
# depending on what's available in the compas.scene.SceneObject classes

scene = Scene()
mesh = Mesh.from_off(compas.get("tubemesh.off"))
scene.add(mesh)
for i in range(5):
    for j in range(5):
        scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            name=f"Box_{i}_{j}",
        )

viewer = Viewer()
viewer.scene = scene
viewer.show()
