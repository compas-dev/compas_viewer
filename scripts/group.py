from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Translation
from compas_viewer import Viewer
from compas_viewer.scene import Tag

box1 = Box.from_width_height_depth(5, 1, 1)
box2 = Box.from_width_height_depth(1, 5, 1)
t = Tag("EN", (0, 0, 0), height=50)
viewer = Viewer()

# Simple list of objects
group1 = viewer.scene.add([box1, box2, t])


# with kwargs for each object
box1 = box1.transformed(Translation.from_vector([0, 5, 0]))
box2 = box2.transformed(Translation.from_vector([0, 5, 0]))
group2 = viewer.scene.add([(box1, {"name": "box1", "facecolor": Color.red()}), (box2, {"name": "box2", "facecolor": Color.green()})], linecolor=Color.blue())

# with nested groups
box1 = box1.transformed(Translation.from_vector([0, 5, 0]))
box2 = box2.transformed(Translation.from_vector([0, 5, 0]))
group3 = viewer.scene.add([[box1], box2])
group3.transformation = Translation.from_vector([0, 0, 5])
viewer.show()
