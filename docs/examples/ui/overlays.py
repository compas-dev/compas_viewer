from compas.colors import Color
from compas.geometry import Box
from compas_viewer import LegendOverlay
from compas_viewer import ScaleBarOverlay
from compas_viewer import ScreenTextOverlay
from compas_viewer import Viewer
from compas_viewer.config import Config

config = Config()
config.measurement.unit = "m"
config.measurement.precision = 2

viewer = Viewer(config=config)

viewer.scene.add(Box(1), surfacecolor=Color.red())

viewer.add_overlay(ScaleBarOverlay())
viewer.add_overlay(
    LegendOverlay(
        [
            ("Structure", Color.red()),
            ("Context", Color.grey()),
        ],
        title="Objects",
    )
)

title = ScreenTextOverlay(
    "Structural model",
    position=(0.5, 0.04),
    horizontal_alignment="center",
    vertical_alignment="top",
    color=Color.white(),
)
viewer.add_overlay(title)

temporary_note = ScreenTextOverlay(
    "Draft",
    position=(0.98, 0.98),
    horizontal_alignment="right",
    vertical_alignment="bottom",
)
viewer.add_overlay(temporary_note)
viewer.remove_overlay(temporary_note)

viewer.show()
