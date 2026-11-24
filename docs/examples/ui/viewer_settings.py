from PySide6.QtCore import QTimer

from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Translation
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import TextAnnotation
from compas_viewer import Viewer
from compas_viewer.config import Config
from compas_viewer.uidefinitions import default_settings_items

config = Config()
config.camera.target = [1.5, 1.0, 0.0]
config.camera.position = [7.0, 8.0, 5.0]
config.renderer.show_grid = True
config.measurement.unit = "m"
config.measurement.precision = 2

settings_items = default_settings_items()
viewer = Viewer(config=config, settings_items=settings_items)

viewer.scene.add(
    Box(2.0, 2.0, 2.0, Frame.worldXY()),
    name="Tutorial box",
    surfacecolor=Color(0.2, 0.55, 0.9),
)

mesh = Mesh.from_vertices_and_faces(
    [[0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [3.0, 2.0, 0.0], [0.0, 2.0, 0.0]],
    [[0, 1, 2, 3]],
)
viewer.scene.add(
    mesh,
    name="Tutorial mesh",
    transformation=Translation.from_vector([2.5, 0.0, 0.0]),
    show_vertices=False,
    show_edges=True,
)

viewer.scene.add_annotation(
    TextAnnotation("Scene, Data, and Annotations", (0.0, -1.5, 1.5), height=24),
    name="Tutorial label",
)
viewer.scene.add_annotation(
    DistanceDimension(
        PointAnchor((0.0, 0.0, 0.0)),
        PointAnchor((3.0, 0.0, 0.0)),
        unit=config.measurement.unit,
        precision=config.measurement.precision,
    ),
    name="Tutorial distance",
)


def open_camera_settings() -> None:
    """Open the reusable settings window focused on Camera."""
    viewer.ui.settings.show("Camera")


QTimer.singleShot(0, open_camera_settings)
viewer.show()
