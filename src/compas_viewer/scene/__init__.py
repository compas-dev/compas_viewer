"""
The Viewer implemeation of scene and scene objects are here.
"""


from compas.plugins import plugin
from compas.scene import register

from compas.geometry import Box
from compas.geometry import Sphere

from .sceneobject import ViewerSceneObject
from .boxobject import BoxObject
from .sphereobject import SphereObject


@plugin(category="drawing-utils", requires=["compas_viewer"])
def clear(guids=None):
    pass


@plugin(category="drawing-utils", requires=["compas_viewer"])
def redraw():
    pass


@plugin(category="factories", requires=["compas_viewer"])
def register_scene_objects():
    register(Box, BoxObject, context="Viewer")
    register(Sphere, SphereObject, context="Viewer")
    # register other scene objects here


__all__ = [
    "ViewerSceneObject",
    "BoxObject",
    "SphereObject",
]
