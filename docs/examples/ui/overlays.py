from compas.colors import Color
from compas.geometry import Box
from compas_viewer import LegendOverlay
from compas_viewer import ScaleBarOverlay
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

viewer.show()
