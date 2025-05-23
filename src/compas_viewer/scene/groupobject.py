from compas.data import Data

from .sceneobject import ViewerSceneObject


class Group(Data):
    """A group of compas.data.Data items."""

    def __init__(self, items: list[Data] = None):
        super().__init__()
        self.items = items or []

    @property
    def __data__(self):
        return {"items": self.items}


class GroupObject(ViewerSceneObject):
    """A group of scene objects."""

    def __init__(self, item=None, **kwargs):
        super().__init__(item=Group(item), **kwargs)
        for item in self.items:
            if isinstance(item, (Data, list)):
                self.add(item, **kwargs)
            elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], (Data, list)):
                item_kwargs = kwargs.copy()
                item_kwargs.update(item[1])
                self.add(item[0], **item_kwargs)
            else:
                print(item)
                raise TypeError("Group items must be of type `Data` or a tuple of (`Data`, kwargs).")

    @property
    def items(self):
        return self.item.items

    def init(self, *args, **kwargs):
        pass
