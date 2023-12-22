from compas.geometry import Box
from compas.scene.context import _detect_current_context

from compas_viewer import Viewer
from compas_viewer.scene.sceneobject import SceneObject
from compas_viewer.scene.meshobject import MeshObject

viewer = Viewer()
mesh = SceneObject(MeshObject, is_selected=True)


print(type(mesh))
# print(_detect_current_context())

# viewer.show()
