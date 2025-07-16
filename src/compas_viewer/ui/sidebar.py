from compas_viewer.components import Sceneform
from compas_viewer.components.camerasetting import CameraSetting
from compas_viewer.components.container import Container
from compas_viewer.components.objectsetting import ObjectSetting
from compas_viewer.components.tabform import Tabform


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
    tabform : Tabform
        TabForm component containing ObjectSetting and CameraSetting, if they are in the items list.
    object_setting : ObjectSetting
        ObjectSetting component nested within the TabForm, if it is in the items list.
    camera_setting : CameraSetting
        CameraSetting component nested within the TabForm, if it is in the items list.

    """

    def __init__(self) -> None:
        super().__init__(container_type="splitter")
        self.tabform = Tabform(tab_position="top")
        self.load_items()

    @property
    def items(self):
        return self.viewer.config.ui.sidebar.items

    def load_items(self):
        tabform_added = False

        for item in self.items:
            itemtype = item.get("type", None)

            if itemtype == "Sceneform":
                columns = item.get("columns", None)
                if columns is None:
                    raise ValueError("Please setup config for Sceneform")
                self.sceneform = Sceneform(columns=columns)
                self.add(self.sceneform)

            if itemtype == "ObjectSetting":
                self.object_setting = ObjectSetting()
                self.tabform.add_tab("Object", container=self.object_setting)
                if not tabform_added:
                    self.add(self.tabform)
                    tabform_added = True

            if itemtype == "CameraSetting":
                self.camera_setting = CameraSetting()
                self.tabform.add_tab("Camera", container=self.camera_setting)
                if not tabform_added:
                    self.add(self.tabform)
                    tabform_added = True
