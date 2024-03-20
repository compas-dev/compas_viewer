from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame

from compas_viewer import Viewer
from compas_viewer.layout import Treeform

viewer = Viewer(rendermode="shaded")

for i in range(10):
    for j in range(10):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
            show_points=False,
            show_lines=True,
            surfacecolor=Color(i / 10, j / 10, 0.0),
            name=f"Box_{i}_{j}",
        )

form_ids = Treeform(viewer.scene.tree, {"Name": (lambda o: o.object.name), "Object": (lambda o: o.object)})
viewer.layout.viewport.add_element(form_ids)
form_colors = Treeform(
    viewer.scene.tree,
    {"Name": (lambda o: o.object.name), "Object-Color": (lambda o: o.object.surfacecolor)},
    backgrounds={"Object-Color": (lambda o: o.object.surfacecolor)},
)
viewer.layout.viewport.add_element(form_colors, False)

viewer.show()
