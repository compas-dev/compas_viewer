from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer import Viewer

viewer = Viewer()

left = viewer.scene.add(
    Box(1.0),
    name="Left box",
    transformation=Translation.from_vector([-2.0, 0.0, 0.0]),
)
right = viewer.scene.add(
    Box(1.0),
    name="Right box",
    transformation=Translation.from_vector([2.0, 0.0, 0.0]),
)

# Apply one world-space delta to both objects as a single transaction.
viewer.transform_objects(
    (left, right),
    Translation.from_vector([0.0, 0.0, 2.0]),
)

# Undo and redo operate on the complete transaction.
viewer.undo()
viewer.redo()

viewer.show()
