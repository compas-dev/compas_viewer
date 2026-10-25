from typing import TYPE_CHECKING
from typing import cast

from compas_viewer.components import SceneTree
from compas_viewer.components.camerasetting import CameraSetting
from compas_viewer.components.container import Container
from compas_viewer.components.displaysetting import DisplaySetting
from compas_viewer.components.objectsetting import ObjectSetting
from compas_viewer.components.sceneform import SceneColumn
from compas_viewer.components.tabform import Tabform
from compas_viewer.uidefinitions import UIItem

if TYPE_CHECKING:
    from .viewport import ViewPort


class SideBarRight(Container):
    """Display the scene tree and viewer settings beside the viewport."""

    def __init__(self, viewport: "ViewPort") -> None:
        super().__init__(container_type="splitter")
        self.viewport = viewport
        self.tabform = Tabform(tab_position="top")
        self.load_items()
        self.widget.setMinimumWidth(self.viewer.config.ui.sidebar.minimum_width)
        self.widget.setSizes([360, 240])
        if self.widget.count() > 0:
            self.widget.setStretchFactor(0, 3)
        if self.widget.count() > 1:
            self.widget.setStretchFactor(1, 2)

    @property
    def items(self) -> list[UIItem]:
        """list[UIItem]: Runtime sidebar item definitions."""
        return self.viewer.sidebar_items

    def load_items(self) -> None:
        """Populate the sidebar from its configuration."""
        tabform_added = False

        for item in self.items:
            itemtype = item.get("type", None)

            if itemtype in {"SceneTree", "Sceneform"}:
                columns = item.get("columns", None)
                if columns is None:
                    raise ValueError("Please setup config for Sceneform")
                self.sceneform = SceneTree(columns=cast(list[SceneColumn], columns))
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

            if itemtype == "DisplaySetting":
                self.display_setting = DisplaySetting(self.viewport)
                self.tabform.add_tab("Display", container=self.display_setting)
                if not tabform_added:
                    self.add(self.tabform)
                    tabform_added = True
