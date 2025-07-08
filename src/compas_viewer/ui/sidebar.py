from typing import Callable
from compas_viewer.components import Sceneform
from compas_viewer.components.objectsetting import ObjectSetting
from compas_viewer.components.container import Container


class SideBarRight(Container):
    """Sidebar for the right side of the window, containing commonly used forms like sceneform and objectsetting.

    Parameters
    ----------
    items : list[dict[str, Callable]]
        List of items to be added to the sidebar.

    Attributes
    ----------
    sceneform : Sceneform
        Sceneform component, if it is in the items list.
    object_setting : ObjectSetting
        ObjectSetting component, if it is in the items list.
    """

    def __init__(self, items: list[dict[str, Callable]]) -> None:
        super().__init__(container_type="splitter")
        for item in items:
            itemtype = item.get("type", None)

            if itemtype == "Sceneform":
                columns = item.get("columns", None)
                if columns is None:
                    raise ValueError("Please setup config for Sceneform")
                self.sceneform = Sceneform(columns=columns)
                self.add(self.sceneform)

            if itemtype == "ObjectSetting":
                self.object_setting = ObjectSetting()
                self.add(self.object_setting)
