"""
This package provides scene object plugins for visualizing COMPAS objects in `compas_viewer`.
"""
from compas.scene import register
from compas.plugins import plugin
from .sceneobject import ViewerSceneObject
from compas.datastructures import Mesh


from .meshobject import MeshObject


@plugin(category="drawing-utils", requires=["compas_viewer"])
def clear(guids=None):
    pass


@plugin(category="drawing-utils", requires=["compas_viewer"])
def redraw():
    pass


@plugin(category="factories", requires=["compas_viewer"])
def register_scene_objects():
    register(Mesh, MeshObject, context="Viewer")


__all__ = ["ViewerSceneObject", "MeshObject"]
