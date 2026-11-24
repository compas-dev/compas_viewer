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
from compas_viewer.components.component import Component
from compas_viewer.components.datapanel import DataPanel
from compas_viewer.components.datastructureattributes import DatastructureAttributes
from compas_viewer.components.objectsetting import ObjectSetting
from compas_viewer.components.sceneform import SceneColumn
from compas_viewer.components.sceneform import SceneTree
from compas_viewer.uidefinitions import UIItem
from compas_viewer.uidefinitions import _validate_sidebar_items

if TYPE_CHECKING:
    from .viewport import ViewPort

type SidebarTab = Literal["Scene", "Annotations", "Data"]
type DeletionDomain = Literal["spatial", "annotations"]


class SideBarRight(Component):
    """Display the Scene, Data, and Annotations content domains.

    The sidebar owns content navigation only. Viewer-wide controls belong to
    the separate Viewer Settings window. Scene and Annotations own contextual
    deletion; Data remains read-only.

    """

    TABS: tuple[SidebarTab, ...] = ("Scene", "Data", "Annotations")

    def __init__(self, viewport: "ViewPort") -> None:
        """Construct the closed content domains and consume sidebar definitions."""
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
        """list[UIItem]: Setup-time definitions consumed by this sidebar."""
        return self.viewer.sidebar_items

    def load_items(self) -> None:
        """Populate the three content domains from setup-time definitions.

        Raises
        ------
        ValueError
            If an item type is unsupported or a scene-tree definition omits
            its required columns.

        """
        _validate_sidebar_items(self.items)
        for item in self.items:
            itemtype = item.get("type")
            if itemtype in {"SceneTree", "Sceneform"}:
                columns = item.get("columns")
                self.sceneform = SceneTree(columns=cast(list[SceneColumn], columns))
            elif itemtype == "AnnotationPanel":
                self.annotation_panel = AnnotationPanel()
            elif itemtype == "DataPanel":
                self.data_panel = DataPanel()
            elif itemtype == "ObjectSetting":
                self.object_setting = ObjectSetting()
            elif itemtype == "DatastructureAttributes":
                self.datastructure_attributes = DatastructureAttributes()

        self._compose_scene_page()
        self._compose_annotations_page()
        self._compose_data_page()

    def set_current_tab(self, tab: SidebarTab) -> None:
        """Activate one sidebar domain.

        Parameters
        ----------
        tab
            One of `"Scene"`, `"Data"`, or `"Annotations"`.

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
            Selection domain to remove, or `None` for editor-local and Data
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
        self.widget.update()

    def _compose_scene_page(self) -> None:
        """Compose the Scene hierarchy and optional details inspector."""
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
        """Compose the durable-annotation collection and details inspector."""
        layout = self._page_layouts["Annotations"]
        if hasattr(self, "annotation_panel"):
            layout.addWidget(self.annotation_panel.widget)
        else:
            layout.addWidget(QLabel("No Annotation controls configured"))

    def _compose_data_page(self) -> None:
        """Compose the read-only referenced-data projection."""
        layout = self._page_layouts["Data"]
        if hasattr(self, "data_panel"):
            layout.addWidget(self.data_panel.widget)
        else:
            layout.addWidget(QLabel("No Data controls configured"))

    def _on_tab_changed(self, index: int) -> None:
        """Refresh referenced data when its content domain becomes active."""
        if self.TABS[index] == "Data" and hasattr(self, "data_panel"):
            self.data_panel.update()


__all__ = ["DeletionDomain", "SideBarRight", "SidebarTab"]
