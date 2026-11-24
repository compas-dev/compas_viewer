"""Modeless Viewer-wide settings surface."""

from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import Literal

from PySide6.QtCore import QEvent
from PySide6.QtCore import QObject
from PySide6.QtCore import Qt
from PySide6.QtGui import QHideEvent
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QAbstractSpinBox
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QBoxLayout
from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QFrame
from PySide6.QtWidgets import QGroupBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QTextEdit
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.base import Base
from compas_viewer.components.boundcomponent import BoundComponent
from compas_viewer.components.camerasetting import CameraSetting
from compas_viewer.components.component import Component
from compas_viewer.components.displaysetting import DisplaySetting
from compas_viewer.components.gridunitsetting import GridUnitSetting
from compas_viewer.uidefinitions import UIItem
from compas_viewer.uidefinitions import _validate_settings_items

if TYPE_CHECKING:
    from compas_viewer.components.mainwindow import MainWindow
    from compas_viewer.components.viewport import ViewPort

type SettingsSection = Literal["Camera", "Display", "Grid and Units"]

_EDITOR_TYPES = (QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QComboBox)
_SECTIONS: tuple[SettingsSection, ...] = ("Camera", "Display", "Grid and Units")


class _ViewerSettingsDialog(QDialog):
    """Own settings-local Escape handling and main-window teardown."""

    def __init__(self, parent: QWidget, release_resources: Callable[[], None]) -> None:
        """Initialize a non-modal dialog owned by `parent`."""
        super().__init__(parent)
        self._owner = parent
        self._release_resources: Callable[[], None] | None = release_resources
        self._owner.installEventFilter(self)
        self.setWindowTitle("Viewer Settings")
        self.setAccessibleName("Viewer Settings")
        self.setObjectName("viewerSettingsWindow")
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setModal(False)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Own window-level Escape while settings are visible."""
        super().showEvent(event)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        """Release the temporary application event filter when hidden."""
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        super().hideEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Route owner teardown and settings-local Escape events."""
        owner = getattr(self, "_owner", None)
        if owner is not None and watched is owner and event.type() == QEvent.Type.Close:
            self._teardown()
            return False
        if not (
            self.isVisible()
            and event.type() == QEvent.Type.KeyPress
            and isinstance(event, QKeyEvent)
            and event.key() == Qt.Key.Key_Escape
            and event.modifiers() == Qt.KeyboardModifier.NoModifier
        ):
            return False

        popup = QApplication.activePopupWidget()
        if popup is not None and self._owns(popup):
            popup.hide()
            event.accept()
            return True
        if QApplication.activeWindow() is not self or isinstance(QApplication.focusWidget(), _EDITOR_TYPES):
            return False

        self.hide()
        event.accept()
        return True

    def _owns(self, widget: QWidget) -> bool:
        """Return whether `widget` belongs to this settings window."""
        current: QWidget | None = widget
        while current is not None:
            if current is self:
                return True
            current = current.parentWidget()
        return False

    def _teardown(self) -> None:
        """Release the settings window when its owning Viewer closes."""
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        self._owner.removeEventFilter(self)
        self.hide()
        release_resources = self._release_resources
        self._release_resources = None
        if release_resources is not None:
            release_resources()
        self.deleteLater()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Keep Escape in focused editors and hide for window-level use."""
        if event.key() == Qt.Key.Key_Escape and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            if isinstance(self.focusWidget(), _EDITOR_TYPES):
                event.accept()
                return
            self.hide()
            event.accept()
            return
        super().keyPressEvent(event)


class ViewerSettings(Base):
    """Own one reusable modeless Viewer Settings window.

    The window is constructed once per Viewer and starts hidden. Each call to
    `show` refreshes the configured controls before showing and raising the
    same Qt dialog. Closing the dialog hides it for reuse; closing the main
    Viewer releases it. Window visibility, geometry, scroll position, and the
    focused section are transient and are not part of Viewer configuration.

    Escape belongs to the active settings window without replacing the main
    Viewer's measurement-cancel and deselection behavior. Focused editors and
    owned popups retain their local Escape behavior.

    Parameters
    ----------
    window
        Main Viewer window that owns the settings window.
    viewport
        Viewport supplying the existing camera and display settings context.

    """

    def __init__(self, window: "MainWindow", viewport: "ViewPort") -> None:
        """Construct the hidden settings window and consume its item definitions."""
        self.viewport = viewport
        self.widget = _ViewerSettingsDialog(window.widget, self._release_resources)
        self.widget.setMinimumSize(420, 480)

        outer = QVBoxLayout(self.widget)
        outer.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(self.scroll)

        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(14)
        self.scroll.setWidget(self.content)
        self.sections: dict[SettingsSection, tuple[QGroupBox, Component]] = {}
        self.load_items()
        self.widget.hide()

    @property
    def items(self) -> list[UIItem]:
        """list[UIItem]: Setup-time definitions consumed by this window."""
        return self.viewer.settings_items

    def load_items(self) -> None:
        """Populate the settings window from its setup-time definitions.

        Raises
        ------
        ValueError
            If a definition has an unsupported or duplicate item type.

        """
        _validate_settings_items(self.items)
        for item in self.items:
            itemtype = item.get("type")
            if itemtype == "CameraSetting":
                self.camera_setting = CameraSetting(self.viewport)
                self.add_section("Camera", self.camera_setting)
            elif itemtype == "DisplaySetting":
                self.display_setting = DisplaySetting(self.viewport)
                self.add_section("Display", self.display_setting)
            elif itemtype == "GridUnitSetting":
                self.grid_unit_setting = GridUnitSetting()
                self.add_section("Grid and Units", self.grid_unit_setting)

    def add_section(self, name: SettingsSection, component: Component) -> None:
        """Add one labeled Viewer Settings section.

        Parameters
        ----------
        name
            Closed section identifier.
        component
            Settings component displayed in the section.

        Raises
        ------
        ValueError
            If `name` is already configured.

        """
        if name in self.sections:
            raise ValueError(f"Viewer Settings section {name!r} already exists.")
        group = QGroupBox(name)
        group.setObjectName("viewerSettingsSection")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(6, 12, 6, 12)
        layout.addWidget(component.widget)
        self._fit_component(component)
        self.layout.addWidget(group)
        self.sections[name] = (group, component)
        self._align_field_columns()

    def show(self, section: SettingsSection | None = None) -> None:
        """Refresh and show the reusable window, optionally focusing a section.

        Parameters
        ----------
        section
            `"Camera"`, `"Display"`, or `"Grid and Units"` to reveal after
            opening. `None` leaves the current scroll position unchanged.

        Raises
        ------
        ValueError
            If `section` is unsupported or absent from the setup-time
            composition.

        """
        if section is not None and section not in _SECTIONS:
            raise ValueError(f"Unsupported Viewer Settings section: {section!r}.")
        if section is not None and section not in self.sections:
            raise ValueError(f"Viewer Settings section {section!r} is not configured.")

        self.update()
        self.widget.show()
        self.widget.raise_()
        self.widget.activateWindow()
        if section is not None:
            self.focus_section(section)

    def focus_section(self, name: SettingsSection) -> None:
        """Scroll one configured settings section into view.

        Parameters
        ----------
        name
            Section to reveal.

        Raises
        ------
        ValueError
            If the settings window does not contain `name`.

        """
        try:
            group, _component = self.sections[name]
        except KeyError:
            raise ValueError(f"Viewer Settings section {name!r} is not configured.") from None
        self.scroll.ensureWidgetVisible(group)
        group.setFocus(Qt.FocusReason.OtherFocusReason)

    def update(self) -> None:
        """Update every configured Viewer Settings section."""
        for _group, component in self.sections.values():
            component.update()
            self._fit_component(component)
        self._align_field_columns()
        self.widget.update()

    def _release_resources(self) -> None:
        """Stop settings-bound watchers before their widgets are deleted."""
        for _group, component in self.sections.values():
            self._stop_watchers(component)

    @classmethod
    def _stop_watchers(cls, component: Component) -> None:
        """Stop watchers in one settings component tree."""
        if isinstance(component, BoundComponent):
            component.stop_watching()
        for child in getattr(component, "children", ()):
            cls._stop_watchers(child)

    def _align_field_columns(self) -> None:
        """Align labels and editors across configured settings sections."""
        rows: list[tuple[QLabel, QWidget, QBoxLayout]] = []
        for _group, component in self.sections.values():
            for child in getattr(component, "children", ()):
                label = getattr(child, "label", None)
                layout = child.widget.layout()
                if not isinstance(label, QLabel) or not isinstance(layout, QBoxLayout) or layout.count() < 2:
                    continue
                field_item = layout.itemAt(1)
                if field_item is None:
                    continue
                field = field_item.widget()
                if field is not None:
                    rows.append((label, field, layout))
        if not rows:
            return

        label_width = max(label.sizeHint().width() for label, _field, _layout in rows)
        for label, field, layout in rows:
            label.setFixedWidth(label_width)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            field.setAttribute(Qt.WidgetAttribute.WA_LayoutUsesWidgetRect, True)
            field.setMaximumWidth(16_777_215)
            field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            layout.setStretch(0, 0)
            layout.setStretch(1, 1)

    @staticmethod
    def _fit_component(component: Component) -> None:
        """Let the outer settings window own scrolling."""
        widget = component.widget
        if not isinstance(widget, QScrollArea):
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            return
        widget.setFrameShape(QFrame.Shape.NoFrame)
        widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        contents = widget.widget()
        if contents is not None:
            contents.adjustSize()
            widget.setFixedHeight(contents.sizeHint().height())
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)


__all__ = ["SettingsSection", "ViewerSettings"]
