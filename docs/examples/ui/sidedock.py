from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.components import Button
from compas_viewer.components import Component
from compas_viewer.components import Slider

viewer = Viewer()
box = viewer.scene.add(Box(1))


def toggle_box() -> None:
    box.show = not box.show
    viewer.renderer.update()


def move_box(_component: Component, value: float) -> None:
    box.transformation = Translation.from_vector([5 * value, 0, 0])
    box.update()
    viewer.renderer.update()


def update_box(_component: Component, _value: float) -> None:
    box.update()
    viewer.renderer.update()


viewer.ui.sidedock.show = True
viewer.ui.sidedock.add(Button(text="Toggle Box", action=toggle_box))
viewer.ui.sidedock.add(Slider(title="Move Box", min_val=0, max_val=2, step=0.2, action=move_box))
viewer.ui.sidedock.add(Slider(title="Box Opacity", obj=box, attr="opacity", min_val=0, max_val=1, step=0.1, action=update_box))

viewer.show()
