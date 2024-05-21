from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer import Viewer

box1 = Box.from_width_height_depth(5, 1, 1)
box2 = Box.from_width_height_depth(1, 5, 1)

viewer = Viewer()

# Simple list of objects
group1 = viewer.scene.add([box1, box2])


# with kwargs for each object
box1 = box1.transformed(Translation.from_vector([0, 5, 0]))
box2 = box2.transformed(Translation.from_vector([0, 5, 0]))
group2 = viewer.scene.add([(box1, {"name": "box1", "facecolor": Color.red()}), (box2, {"name": "box2", "facecolor": Color.green()})], linecolor=Color.blue())

# with nested groups
box1 = box1.transformed(Translation.from_vector([0, 5, 0]))
box2 = box2.transformed(Translation.from_vector([0, 5, 0]))
group3 = viewer.scene.add([[box1], box2])
viewer.show()
