from typing import TYPE_CHECKING
from typing import Literal
from typing import cast

from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.components.annotationpanel import AnnotationPanel
from compas_viewer.components.camerasetting import CameraSetting
from compas_viewer.components.component import Component
from compas_viewer.components.datastructureattributes import DatastructureAttributes
from compas_viewer.components.displaysetting import DisplaySetting
from compas_viewer.components.measurementsetting import MeasurementSetting
from compas_viewer.components.objectsetting import ObjectSetting
from compas_viewer.components.sceneform import SceneColumn
from compas_viewer.components.sceneform import SceneTree
from compas_viewer.components.systempanel import SystemPanel
from compas_viewer.components.systempanel import SystemSection
from compas_viewer.uidefinitions import UIItem

if TYPE_CHECKING:
    from .viewport import ViewPort

SidebarTab = Literal["Scene", "Annotations", "System"]


class SideBarRight(Component):
    """Display Scene, Annotations, and System in stable sidebar domains."""

    TABS: tuple[SidebarTab, ...] = ("Scene", "Annotations", "System")

    def __init__(self, viewport: "ViewPort") -> None:
        super().__init__()
        self.viewport = viewport
        self.widget = QTabWidget()
        self.widget.setMinimumWidth(self.viewer.config.ui.sidebar.minimum_width)
        self.pages: dict[SidebarTab, QWidget] = {}
        self._page_layouts: dict[SidebarTab, QVBoxLayout] = {}
        for name in self.TABS:
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(0, 0, 0, 0)
            self.pages[name] = page
            self._page_layouts[name] = layout
            self.widget.addTab(page, name)
        self.load_items()
        self.set_current_tab("Scene")

    @property
    def items(self) -> list[UIItem]:
        """list[UIItem]: Runtime sidebar item definitions."""
        return self.viewer.sidebar_items

    def load_items(self) -> None:
        """Populate the three sidebar domains from the runtime definitions."""
        for item in self.items:
            itemtype = item.get("type")
            if itemtype in {"SceneTree", "Sceneform"}:
                columns = item.get("columns")
                if columns is None:
                    raise ValueError("Please setup config for Sceneform")
                self.sceneform = SceneTree(columns=cast(list[SceneColumn], columns))
            elif itemtype == "AnnotationPanel":
                self.annotation_panel = AnnotationPanel()
            elif itemtype == "ObjectSetting":
                self.object_setting = ObjectSetting()
            elif itemtype == "DatastructureAttributes":
                self.datastructure_attributes = DatastructureAttributes()
            elif itemtype == "CameraSetting":
                self.camera_setting = CameraSetting()
            elif itemtype == "DisplaySetting":
                self.display_setting = DisplaySetting(self.viewport)
            elif itemtype == "MeasurementSetting":
                self.measurement_setting = MeasurementSetting()

        self._compose_scene_page()
        self._compose_annotations_page()
        self._compose_system_page()

    def set_current_tab(self, tab: SidebarTab) -> None:
        """Activate one sidebar domain.

        Parameters
        ----------
        tab
            One of `"Scene"`, `"Annotations"`, or `"System"`.

        Raises
        ------
        ValueError
            If `tab` is not a supported sidebar domain.

        """
        if tab not in self.TABS:
            raise ValueError(f"Unsupported sidebar tab: {tab!r}.")
        self.widget.setCurrentIndex(self.TABS.index(tab))

    def focus_system_section(self, section: SystemSection) -> None:
        """Activate System and reveal one configured settings section.

        Parameters
        ----------
        section
            One of `"Camera"`, `"Display"`, or `"Units and Measurement"`.

        Raises
        ------
        ValueError
            If `section` is unsupported or not configured.

        """
        if section not in {"Camera", "Display", "Units and Measurement"}:
            raise ValueError(f"Unsupported system section: {section!r}.")
        self.set_current_tab("System")
        self.system_panel.focus_section(section)

    def update_spatial_selection(self) -> None:
        """Update only Scene controls affected by spatial selection."""
        if hasattr(self, "sceneform"):
            self.sceneform.update()
        if hasattr(self, "object_setting"):
            self.object_setting.update()
        if hasattr(self, "datastructure_attributes"):
            self.datastructure_attributes.update()

    def update_annotation_selection(self) -> None:
        """Update only controls affected by annotation selection."""
        if hasattr(self, "annotation_panel"):
            self.annotation_panel.update()

    def update(self) -> None:
        """Update every configured sidebar domain."""
        self.update_spatial_selection()
        self.update_annotation_selection()
        self.system_panel.update()
        self.widget.update()

    def _compose_scene_page(self) -> None:
        layout = self._page_layouts["Scene"]
        if hasattr(self, "sceneform"):
            layout.addWidget(self.sceneform.widget, 3)

        details: list[tuple[str, Component]] = []
        if hasattr(self, "object_setting"):
            details.append(("Object", self.object_setting))
        if hasattr(self, "datastructure_attributes"):
            details.append(("Attributes", self.datastructure_attributes))

        if len(details) == 1:
            layout.addWidget(details[0][1].widget, 2)
        elif len(details) > 1:
            self.scene_details = QTabWidget()
            for name, component in details:
                self.scene_details.addTab(component.widget, name)
            layout.addWidget(self.scene_details, 2)
        elif not hasattr(self, "sceneform"):
            layout.addWidget(QLabel("No Scene controls configured"))

    def _compose_annotations_page(self) -> None:
        layout = self._page_layouts["Annotations"]
        if hasattr(self, "annotation_panel"):
            layout.addWidget(self.annotation_panel.widget)
        else:
            layout.addWidget(QLabel("No Annotation controls configured"))

    def _compose_system_page(self) -> None:
        layout = self._page_layouts["System"]
        self.system_panel = SystemPanel()
        if hasattr(self, "camera_setting"):
            self.system_panel.add_section("Camera", self.camera_setting)
        if hasattr(self, "display_setting"):
            self.system_panel.add_section("Display", self.display_setting)
        if hasattr(self, "measurement_setting"):
            self.system_panel.add_section("Units and Measurement", self.measurement_setting)
        layout.addWidget(self.system_panel.widget)


__all__ = ["SideBarRight", "SidebarTab"]
