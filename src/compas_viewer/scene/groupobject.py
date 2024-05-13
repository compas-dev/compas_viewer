from compas.data import Data
from compas.scene.sceneobject import SceneObject


class Group(Data):
    """A group of compas.data.Data items."""

    def __init__(self, items):
        super().__init__()
        self.items = items


class GroupObject(SceneObject):
    """A group of scene objects."""

    def __init__(self, items, **kwargs):
        super().__init__(Group(items), **kwargs)
        self.is_visible = True
        self.is_selected = False
        self.opacity = 1.0
        self.bounding_box = None

        for item in items:
            if isinstance(item, (Data, list)):
                self.add(item, **kwargs)
            elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], (Data, list)):
                self.add(item[0], **item[1])
            else:
                print(item)
                raise TypeError("Group items must be of type `Data` or a tuple of (`Data`, kwargs).")

    def init(self, *args, **kwargs):
        pass

    def draw(self, *args, **kwargs):
        pass

    def draw_instance(self, *args, **kwargs):
        pass
