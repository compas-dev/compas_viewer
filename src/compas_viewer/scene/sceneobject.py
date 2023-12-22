from compas.scene import SceneObject


class ViewerSceneObject(SceneObject):
    """Base class for all Viewer scene objects."""

    def __init__(self, **kwargs):
        super(ViewerSceneObject, self).__init__(**kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.geometry})"