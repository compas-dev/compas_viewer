from compas.colors import Color
from compas.scene import ArrowAnnotation
from compas.scene import DimensionStyle
from compas.scene import DistanceDimension
from compas.scene import PointAnchor
from compas.scene import TextAnnotation
from compas_viewer import Viewer

viewer = Viewer()
viewer.scene.add_annotation(
    TextAnnotation(
        "Screen-sized annotation",
        (0, 0, 0),
        height=24,
        horizontal_alignment="center",
    ),
    name="Screen label",
)
viewer.scene.add_annotation(
    TextAnnotation("World-sized annotation", (0, 2, 0), height=0.5, height_mode="world"),
    name="World label",
)
viewer.scene.add_annotation(ArrowAnnotation((0, 0, 0), (3, 0, 0)), name="Direction")
viewer.scene.add_annotation(
    DistanceDimension(
        PointAnchor((0, 0, 0)),
        PointAnchor((3, 0, 0)),
        unit="m",
        precision=2,
    ),
    name="Length",
    style=DimensionStyle(
        color=Color(0.0, 0.75, 1.0),
        line_width=4.0,
        text_size=16.0,
        arrow_size=14.0,
        label_offset=10.0,
    ),
)
viewer.show()
