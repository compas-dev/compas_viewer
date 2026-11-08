from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.components import Button
from compas_viewer.components import Component
from compas_viewer.components import Slider
from compas_viewer.config import Config

config = Config()
config.ui.sidedock.show = True

viewer = Viewer(config=config)
box_object = viewer.scene.add(Box(1))


def toggle_box() -> None:
    box_object.show = not box_object.show
    viewer.refresh_appearance((box_object,))


def move_box(_component: Component, value: float) -> None:
    box_object.transformation = Translation.from_vector([5 * value, 0, 0])
    viewer.refresh_transform((box_object,))


def refresh_viewer(_component: Component, _value: float) -> None:
    viewer.refresh_appearance((box_object,))


viewer.ui.sidedock.add(Button(text="Toggle Box", action=toggle_box))
viewer.ui.sidedock.add(Slider(title="Move Box", min_val=0, max_val=2, step=0.2, action=move_box))
viewer.ui.sidedock.add(Slider(title="Box Opacity", obj=box_object, attr="opacity", min_val=0, max_val=1, step=0.1, action=refresh_viewer))

viewer.show()
