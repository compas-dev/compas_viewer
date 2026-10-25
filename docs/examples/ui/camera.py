from collections.abc import Callable

from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer import Viewer
from compas_viewer.components import Component
from compas_viewer.components import Slider

viewer = Viewer()
viewer.renderer.camera.target = [2, 2, 0]
viewer.renderer.camera.position = [2, 10, 5]

for x in range(5):
    for y in range(5):
        viewer.scene.add(
            Box(0.5, 0.5, 0.5, Frame([x, y, 0], [1, 0, 0], [0, 1, 0])),
            surfacecolor=Color(x / 5, y / 5, 0),
        )


def camera_control(target: object, attribute: str) -> Callable[[Component, float], None]:
    def update(_component: Component, value: float) -> None:
        setattr(target, attribute, value)
        viewer.renderer.update()

    return update


viewer.ui.sidedock.show = True
for title, vector in (("Position", viewer.renderer.camera.position), ("Target", viewer.renderer.camera.target)):
    for axis in ("x", "y", "z"):
        viewer.ui.sidedock.add(
            Slider(
                value=getattr(vector, axis),
                title=f"{title} {axis.upper()}",
                min_val=-10,
                max_val=10,
                action=camera_control(vector, axis),
            )
        )

viewer.show()
