from compas.scene import ArrowAnnotation
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import TextAnnotation
from compas_viewer import Viewer

viewer = Viewer()
viewer.scene.add(
    TextAnnotation(
        "Screen-sized annotation",
        (0, 0, 0),
        height=24,
        horizontal_alignment="center",
    )
)
viewer.scene.add(TextAnnotation("World-sized annotation", (0, 2, 0), height=0.5, height_mode="world"))
viewer.scene.add(ArrowAnnotation((0, 0, 0), (3, 0, 0)))
viewer.scene.add(
    DistanceDimension(
        PointAnchor((0, 0, 0)),
        PointAnchor((3, 0, 0)),
        unit="m",
        precision=2,
    )
)
viewer.show()
