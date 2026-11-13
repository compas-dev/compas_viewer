from typing import TYPE_CHECKING
from typing import Literal
from typing import cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractSpinBox
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.components.annotationpanel import AnnotationPanel
from compas_viewer.components.camerasetting import CameraSetting
from compas_viewer.components.component import Component
from compas_viewer.components.datapanel import DataPanel
from compas_viewer.components.datastructureattributes import DatastructureAttributes
from compas_viewer.components.displaysetting import DisplaySetting
from compas_viewer.components.gridunitsetting import GridUnitSetting
from compas_viewer.components.objectsetting import ObjectSetting
from compas_viewer.components.sceneform import SceneColumn
from compas_viewer.components.sceneform import SceneTree
from compas_viewer.components.systempanel import SystemPanel
from compas_viewer.components.systempanel import SystemSection
from compas_viewer.uidefinitions import UIItem

if TYPE_CHECKING:
    from .viewport import ViewPort

SidebarTab = Literal["Scene", "Annotations", "Data", "System"]
DeletionDomain = Literal["spatial", "annotations"]


class SideBarRight(Component):
    """Display Scene, Annotations, Data, and System sidebar domains."""

    TABS: tuple[SidebarTab, ...] = ("Scene", "Data", "Annotations", "System")

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
        self.widget.currentChanged.connect(self._on_tab_changed)
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
            elif itemtype == "DataPanel":
                self.data_panel = DataPanel()
            elif itemtype == "ObjectSetting":
                self.object_setting = ObjectSetting()
            elif itemtype == "DatastructureAttributes":
                self.datastructure_attributes = DatastructureAttributes()
            elif itemtype == "CameraSetting":
                self.camera_setting = CameraSetting(self.viewport)
            elif itemtype == "DisplaySetting":
                self.display_setting = DisplaySetting(self.viewport)
            elif itemtype == "GridUnitSetting":
                self.grid_unit_setting = GridUnitSetting()
            elif itemtype == "MeasurementSetting":
                raise ValueError("Unsupported sidebar item type: 'MeasurementSetting'. Use 'GridUnitSetting'.")

        self._compose_scene_page()
        self._compose_annotations_page()
        self._compose_data_page()
        self._compose_system_page()

    def set_current_tab(self, tab: SidebarTab) -> None:
        """Activate one sidebar domain.

        Parameters
        ----------
        tab
            One of `"Scene"`, `"Annotations"`, `"Data"`, or `"System"`.

        Raises
        ------
        ValueError
            If `tab` is not a supported sidebar domain.

        """
        if tab not in self.TABS:
            raise ValueError(f"Unsupported sidebar tab: {tab!r}.")
        self.widget.setCurrentIndex(self.TABS.index(tab))

    @property
    def current_tab(self) -> SidebarTab:
        """SidebarTab: Active interaction domain."""
        return self.TABS[self.widget.currentIndex()]

    def deletion_domain(self, *, use_focus: bool) -> DeletionDomain | None:
        """Return the selection domain owned by the current interaction context.

        Parameters
        ----------
        use_focus
            Resolve focused Scene, Annotations, viewport, and editor widgets
            before falling back to the active sidebar tab.

        Returns
        -------
        DeletionDomain | None
            Selection domain to remove, or `None` for editor-local and System
            contexts.

        """
        if use_focus:
            focused = QApplication.focusWidget()
            editor_types = (QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox)
            if isinstance(focused, editor_types):
                return None
            if focused is not None:
                annotations = self.pages["Annotations"]
                if focused is annotations or annotations.isAncestorOf(focused):
                    return "annotations"
                scene = self.pages["Scene"]
                renderer = self.viewport.renderer
                if focused is scene or scene.isAncestorOf(focused) or focused is renderer or renderer.isAncestorOf(focused):
                    return "spatial"

        if self.current_tab == "Annotations":
            return "annotations"
        if self.current_tab == "Scene":
            return "spatial"
        return None

    def focus_system_section(self, section: SystemSection) -> None:
        """Activate System and reveal one configured settings section.

        Parameters
        ----------
        section
            One of `"Camera"`, `"Display"`, or `"Grid and Units"`.

        Raises
        ------
        ValueError
            If `section` is unsupported or not configured.

        """
        if section not in {"Camera", "Display", "Grid and Units"}:
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
        if hasattr(self, "data_panel"):
            self.data_panel.update()
        self.system_panel.update()
        self.widget.update()

    def _compose_scene_page(self) -> None:
        layout = self._page_layouts["Scene"]
        details: list[tuple[str, Component]] = []
        if hasattr(self, "object_setting"):
            details.append(("Object", self.object_setting))
        if hasattr(self, "datastructure_attributes"):
            details.append(("Attributes", self.datastructure_attributes))

        detail_widget: QWidget | None = None
        if len(details) == 1:
            detail_widget = details[0][1].widget
        elif len(details) > 1:
            self.scene_details = QTabWidget()
            for name, component in details:
                self.scene_details.addTab(component.widget, name)
            detail_widget = self.scene_details

        if hasattr(self, "sceneform") and detail_widget is not None:
            self.scene_splitter = QSplitter(Qt.Orientation.Vertical)
            self.scene_splitter.setObjectName("sceneInspectorSplitter")
            self.scene_splitter.setChildrenCollapsible(False)
            self.scene_splitter.addWidget(self.sceneform.widget)
            self.scene_splitter.addWidget(detail_widget)
            self.scene_splitter.setCollapsible(0, False)
            self.scene_splitter.setCollapsible(1, False)
            self.scene_splitter.setStretchFactor(0, 3)
            self.scene_splitter.setStretchFactor(1, 2)
            self.sceneform.widget.setMinimumHeight(80)
            detail_widget.setMinimumHeight(80)
            self.scene_splitter.setSizes([300, 200])
            layout.addWidget(self.scene_splitter)
        elif hasattr(self, "sceneform"):
            layout.addWidget(self.sceneform.widget)
        elif detail_widget is not None:
            layout.addWidget(detail_widget)
        elif not hasattr(self, "sceneform"):
            layout.addWidget(QLabel("No Scene controls configured"))

    def _compose_annotations_page(self) -> None:
        layout = self._page_layouts["Annotations"]
        if hasattr(self, "annotation_panel"):
            layout.addWidget(self.annotation_panel.widget)
        else:
            layout.addWidget(QLabel("No Annotation controls configured"))

    def _compose_data_page(self) -> None:
        layout = self._page_layouts["Data"]
        if hasattr(self, "data_panel"):
            layout.addWidget(self.data_panel.widget)
        else:
            layout.addWidget(QLabel("No Data controls configured"))

    def _on_tab_changed(self, index: int) -> None:
        if self.TABS[index] == "Data" and hasattr(self, "data_panel"):
            self.data_panel.update()

    def _compose_system_page(self) -> None:
        layout = self._page_layouts["System"]
        self.system_panel = SystemPanel()
        if hasattr(self, "camera_setting"):
            self.system_panel.add_section("Camera", self.camera_setting)
        if hasattr(self, "display_setting"):
            self.system_panel.add_section("Display", self.display_setting)
        if hasattr(self, "grid_unit_setting"):
            self.system_panel.add_section("Grid and Units", self.grid_unit_setting)
        layout.addWidget(self.system_panel.widget)


__all__ = ["DeletionDomain", "SideBarRight", "SidebarTab"]
