from tkinter import N
from compas.scene.sceneobject import SceneObject


class ViewerObject(SceneObject):
    pass

    def __init__(self):
        self.opacity = None
        self.bounding_box_center = None
        self.matrix = None

    def init(self):
        pass
