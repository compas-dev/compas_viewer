"""
This package provides scene object plugins for visualizing COMPAS objects in `compas_viewer`.
"""
from compas.scene import register
from compas.plugins import plugin

from compas.datastructures import Mesh
from compas.geometry import Box

from .meshobject import MeshObject
from .boxobject import BoxObject


@plugin(category="factories", requires=["Viewer"])
def register_scene_objects():
    register(Mesh, MeshObject, context="Viewer")
    register(Box, BoxObject, context="Viewer")
    print("Viewer SceneObjects registered.")


__all__ = [
    "BoxObject",
    "MeshObject",
]
