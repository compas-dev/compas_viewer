from compas.scene import Group as BaseGroup

from .sceneobject import ViewerSceneObject


class Group(ViewerSceneObject, BaseGroup):
    """A group of scene objects."""

    pass
