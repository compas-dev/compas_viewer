from compas.colors import Color
from compas_viewer import Viewer
from compas_viewer.scene import Tag

viewer = Viewer()
viewer.scene.add(Tag("Left and bottom", (0, 0, 0), height=32))
viewer.scene.add(Tag("Centered", (0, 3, 0), height=32, horizontal_align="center", vertical_align="center"))
viewer.scene.add(Tag("Right and top", (0, 6, 0), height=32, horizontal_align="right", vertical_align="top"))
viewer.scene.add(
    Tag(
        "Multiline\nannotation",
        (4, 3, 0),
        color=Color.white(),
        backgroundcolor=Color(0.1, 0.2, 0.4, 0.8),
        padding=6,
        horizontal_align="center",
    )
)
viewer.scene.add(Tag("World-space height", (8, 0, 0), absolute_height=True, height=1))
viewer.show()
