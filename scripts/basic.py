import compas
from compas.datastructures import Mesh
from compas.geometry import Box
from compas.scene import Scene
from compas.scene.context import _detect_current_context
from compas.scene.context import _get_sceneobject_cls
from compas.scene.context import get_sceneobject_cls

from compas_viewer import Viewer
from compas_viewer.scene.meshobject import MeshObject
from compas_viewer.scene.sceneobject import SceneObject

viewer = Viewer()

mesh = Mesh.from_obj(compas.get("tubemesh.obj"))


viewer.add(mesh)

viewer.show()
