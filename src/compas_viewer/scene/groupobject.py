from compas.data import Data

from .sceneobject import SceneObject


class Group(Data):
    """A group of compas.data.Data items."""

    def __init__(self, items: list[Data] = None):
        super().__init__()
        self.items = items or []

    @property
    def __data__(self):
        return {"items": self.items}


class GroupObject(SceneObject):
    """A group of scene objects."""

    def __init__(self, items, **kwargs):
        super().__init__(Group(items), **kwargs)
        self.show = True
        self.is_selected = False
        self.opacity = 1.0
        self.bounding_box = None

        for item in items:
            if isinstance(item, (Data, list)):
                self.add(item, **kwargs)
            elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], (Data, list)):
                item_kwargs = kwargs.copy()
                item_kwargs.update(item[1])
                self.add(item[0], **item_kwargs)
            else:
                print(item)
                raise TypeError("Group items must be of type `Data` or a tuple of (`Data`, kwargs).")

    def init(self, *args, **kwargs):
        pass

    def draw(self, *args, **kwargs):
        pass

    def draw_instance(self, *args, **kwargs):
        pass
