from compas_viewer.viewer import Viewer
from compas.scene import Scene
from compas.geometry import Box, Translation

scene = Scene()
box = Box()
scene.add(box, color=(255, 0, 0), name="Box1")
group = scene.add_group(name="My Group")
obj2 = scene.add(box, color=(0, 0, 255), name="Box2", parent=group)
obj2.transformation = Translation().from_vector([2, 0, 0])


jsonstring = scene.to_jsonstring(pretty=True)
print(jsonstring)

scene_loaded = Scene.from_jsonstring(jsonstring)

viewer = Viewer()
viewer.scene = scene_loaded

viewer.show()

