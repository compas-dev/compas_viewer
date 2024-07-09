from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer.viewer import Viewer
from compas_viewer.components import Slider

viewer = Viewer()

for i in range(5):
    for j in range(5):
        obj = viewer.scene.add(
            Box(0.5, 0.5, 0.5),
            show_points=True,
            show_lines=True,
            surfacecolor=Color(i / 10, j / 10, 0.0),
            name=f"Box_{i}_{j}",
        )

        obj.transformation =  Frame([i, j, 0], [1, 0, 0], [0, 1, 0]).to_transformation()


def update_renderscale(slider: Slider, value: int):
    viewer.renderer.scale = value
    viewer.renderer.update()
    print(viewer.renderer.scale)


viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(Slider(title="Render Scale", min_val=1, max_val=100, step=1, action=update_renderscale))

viewer.show()
