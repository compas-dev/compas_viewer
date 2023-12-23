from compas.geometry import Box
from compas.scene.context import _detect_current_context

from compas_viewer import Viewer
from compas_viewer.scene.sceneobject import SceneObject
from compas_viewer.scene.meshobject import MeshObject
from compas.datastructures import Mesh

viewer = Viewer()


import compas
from compas.datastructures import Mesh
from compas.scene import Scene

mesh = Mesh.from_obj(compas.get("tubemesh.obj"))

scene = Scene()
scene.clear()
scene.add(mesh)
scene.redraw()
