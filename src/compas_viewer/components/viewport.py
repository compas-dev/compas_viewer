from PySide6.QtCore import QEvent
from PySide6.QtCore import QObject
from PySide6.QtCore import QRect
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction
from PySide6.QtGui import QActionGroup
from PySide6.QtGui import QGuiApplication
from PySide6.QtGui import QHideEvent
from PySide6.QtGui import QIcon
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPaintEvent
from PySide6.QtGui import QResizeEvent
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QSplitter
from PySide6.QtWidgets import QStackedLayout
from PySide6.QtWidgets import QStyle
from PySide6.QtWidgets import QStyleOption
from PySide6.QtWidgets import QStyleOptionToolButton
from PySide6.QtWidgets import QStylePainter
from PySide6.QtWidgets import QToolButton
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.base import Base
from compas_viewer.components.component import Component
from compas_viewer.renderer import Renderer

from .mainwindow import MainWindow
from .sidebar import SideBarRight


class _ViewportMenuButton(QToolButton):
    """Open the private viewport menu without a nested keyboard popup loop."""

    _TEXT_INDICATOR_SPACING = 6

    def _metric_option(self) -> QStyleOptionToolButton:
        """Return a neutral option for state-independent layout metrics."""
        option = QStyleOptionToolButton()
        self.initStyleOption(option)
        option.state &= ~(QStyle.StateFlag.State_Sunken | QStyle.StateFlag.State_On | QStyle.StateFlag.State_MouseOver | QStyle.StateFlag.State_HasFocus)
        return option

    def _frame_option(self) -> QStyleOptionToolButton:
        """Return a native-frame option without Qt's menu indicator or label."""
        option = QStyleOptionToolButton()
        self.initStyleOption(option)
        option.text = ""
        option.icon = QIcon()
        option.features &= ~(
            QStyleOptionToolButton.ToolButtonFeature.Arrow
            | QStyleOptionToolButton.ToolButtonFeature.Menu
            | QStyleOptionToolButton.ToolButtonFeature.PopupDelay
            | QStyleOptionToolButton.ToolButtonFeature.HasMenu
        )
        return option

    def _indicator_extent(self, option: QStyleOptionToolButton) -> int:
        """Return a square indicator extent derived from active style metrics."""
        return max(
            self.style().pixelMetric(QStyle.PixelMetric.PM_MenuButtonIndicator, option, self),
            self.fontMetrics().height(),
        )

    def _presentation_rects(self) -> tuple[QRect, QRect]:
        """Return disjoint text and centered indicator rectangles."""
        option = self._metric_option()
        margin = self.style().pixelMetric(QStyle.PixelMetric.PM_ButtonMargin, option, self)
        frame = self.style().pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth, option, self)
        content = self.rect().adjusted(margin + frame, frame, -(margin + frame), -frame)
        indicator_extent = min(self._indicator_extent(option), content.height())
        indicator_slot = QRect(content.right() - indicator_extent + 1, content.top(), indicator_extent, content.height())
        indicator = QRect(0, 0, indicator_extent, indicator_extent)
        indicator.moveCenter(indicator_slot.center())
        text = QRect(content.left(), content.top(), max(0, indicator_slot.left() - self._TEXT_INDICATOR_SPACING - content.left()), content.height())
        if self.layoutDirection() == Qt.LayoutDirection.RightToLeft:
            text = self.style().visualRect(self.layoutDirection(), content, text)
            indicator = self.style().visualRect(self.layoutDirection(), content, indicator)
        return text, indicator

    def sizeHint(self) -> QSize:  # noqa: N802
        """Reserve one styled row for disjoint label and indicator regions."""
        option = self._metric_option()
        margin = self.style().pixelMetric(QStyle.PixelMetric.PM_ButtonMargin, option, self)
        frame = self.style().pixelMetric(QStyle.PixelMetric.PM_DefaultFrameWidth, option, self)
        text_width = (
            max(
                self.fontMetrics().horizontalAdvance(self.text()),
                self.fontMetrics().boundingRect(self.text()).width(),
                self.fontMetrics().size(Qt.TextFlag.TextSingleLine, self.text()).width(),
            )
            + 2 * frame
        )
        indicator_extent = self._indicator_extent(option)
        content = QSize(
            text_width + self._TEXT_INDICATOR_SPACING + indicator_extent,
            self.fontMetrics().height(),
        )
        styled = self.style().sizeFromContents(QStyle.ContentsType.CT_ToolButton, self._frame_option(), content, self)
        styled.setWidth(max(styled.width(), content.width() + 2 * (margin + frame)))
        styled.setHeight(max(styled.height(), content.height() + 2 * frame))
        return styled.expandedTo(super().sizeHint())

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        """Keep layouts from narrowing the control below its styled hint."""
        return self.sizeHint()

    def paintEvent(self, _event: QPaintEvent) -> None:  # noqa: N802
        """Paint native framing with separate text and centered arrow regions."""
        painter = QStylePainter(self)
        painter.drawComplexControl(QStyle.ComplexControl.CC_ToolButton, self._frame_option())
        text_rect, indicator_rect = self._presentation_rects()
        painter.drawItemText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextSingleLine,
            self.palette(),
            self.isEnabled(),
            self.text(),
            self.foregroundRole(),
        )
        indicator = QStyleOption()
        indicator.initFrom(self)
        indicator.rect = indicator_rect
        painter.drawPrimitive(QStyle.PrimitiveElement.PE_IndicatorArrowDown, indicator)

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Open the menu non-modally for the standard activation keys."""
        if event.key() in {Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down}:
            menu = self.menu()
            if menu is not None:
                menu.popup(self.mapToGlobal(self.rect().bottomLeft()))
                event.accept()
                return
        super().keyPressEvent(event)


class _ViewportMenu(QMenu):
    """Close the private viewport menu deterministically on Escape."""

    cancelled = Signal()

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802
        """Own Escape ahead of the window-global filter while visible."""
        super().showEvent(event)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)

    def hideEvent(self, event: QHideEvent) -> None:  # noqa: N802
        """Release the temporary application event filter after hiding."""
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        super().hideEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Cancel the visible popup before the global Escape command runs."""
        del watched
        if self.isVisible() and event.type() == QEvent.Type.KeyPress and isinstance(event, QKeyEvent) and event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.cancelled.emit()
            event.accept()
            return True
        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        """Treat Escape as an explicit cancellation and hide the popup."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
            self.cancelled.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class _OverlayCanvas(QWidget, Base):
    """Paint transient 2D feedback above the OpenGL renderer."""

    def __init__(self, renderer: Renderer, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.renderer = renderer
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAutoFillBackground(False)

    def sync(self) -> None:
        """Synchronize visibility and schedule one overlay repaint."""
        visible = self.viewer._has_overlay_content()
        self.setVisible(visible)
        if visible:
            self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draw overlays inside the ordinary QWidget paint lifecycle."""
        del event
        if not self.viewer._has_overlay_content():
            return
        painter = QPainter()
        if not painter.begin(self):
            return
        try:
            self.viewer._draw_overlays(self.renderer, painter)
        finally:
            painter.end()


class _ViewControl(QWidget, Base):
    """Provide grouped view and render-mode choices above the renderer."""

    _VIEWS = ("perspective", "top", "front", "right", "ortho")
    _RENDER_MODES = ("shaded", "lighted", "ghosted", "wireframe")

    def __init__(self, renderer: Renderer, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.renderer = renderer
        self.setObjectName("viewport_view_control")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self._button = _ViewportMenuButton(self)
        self._button.setObjectName("viewport_view_menu_button")
        self._button.setText("View / View Mode")
        self._button.setToolTip("View and View Mode")
        self._button.setAccessibleName("View and View Mode")
        self._button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._focus_pending = False
        self._focus_listener_connected = False
        self._focus_window: QWidget | None = None
        self._menu = _ViewportMenu(self._button)
        self._menu.setObjectName("viewport_view_menu")
        self._menu.installEventFilter(self)
        self._menu.cancelled.connect(self._request_renderer_focus)
        self._button.setMenu(self._menu)
        layout.addWidget(self._button)
        self._actions: dict[str, dict[str, QAction]] = {}
        self._add_group("View", "renderer.view", "viewer.change_view", self._VIEWS)
        self._menu.addSeparator()
        self._add_group("View Mode", "renderer.rendermode", "viewer.change_rendermode", self._RENDER_MODES)
        self._menu.aboutToHide.connect(self._request_renderer_focus)
        self.viewer.state.changed.connect(self._on_state_changed)

    def _add_group(self, title: str, state_path: str, command_id: str, values: tuple[str, ...]) -> None:
        """Add one titled exclusive action group to the viewport menu."""
        heading = self._menu.addAction(title)
        heading.setEnabled(False)
        heading.setObjectName(f"viewport_{state_path.replace('.', '_')}_heading")
        group = QActionGroup(self._menu)
        group.setExclusive(True)
        actions = {}
        for value in values:
            action = self._menu.addAction(value.title())
            action.setObjectName(f"viewport_{state_path.replace('.', '_')}_{value}")
            action.setCheckable(True)
            action.setChecked(self.viewer.state.get(state_path) == value)
            action.triggered.connect(lambda _checked=False, selected=value, command=command_id: self.viewer.commands[command](mode=selected))
            group.addAction(action)
            actions[value] = action
        self._actions[state_path] = actions

    def _request_renderer_focus(self) -> None:
        """Request renderer focus after the popup and window are ready."""
        self._focus_pending = True
        window = self.window()
        if not self._focus_listener_connected:
            window.installEventFilter(self)
            app = QGuiApplication.instance()
            if isinstance(app, QGuiApplication):
                app.focusWindowChanged.connect(self._restore_renderer_focus_if_ready)
            self._focus_listener_connected = True
            self._focus_window = window
        self._activate_owner_window()
        QTimer.singleShot(0, self._restore_renderer_focus_if_ready)

    def _activate_owner_window(self) -> None:
        """Request activation of the main window after popup transitions."""
        window = self.window()
        handle = window.windowHandle()
        if handle is not None:
            handle.requestActivate()
        window.activateWindow()

    def _restore_renderer_focus_if_ready(self, *_args: object) -> None:
        """Complete one pending focus request after observable popup teardown."""
        if not self._focus_pending or self._menu.isVisible():
            return
        window = self.window()
        handle = window.windowHandle()
        if handle is None or QGuiApplication.focusWindow() is not handle or not window.isActiveWindow():
            return
        self._clear_focus_request()
        self.renderer.setFocus(Qt.FocusReason.OtherFocusReason)

    def _clear_focus_request(self) -> None:
        """Disconnect the temporary listeners for one focus request."""
        self._focus_pending = False
        if self._focus_listener_connected and self._focus_window is not None:
            self._focus_window.removeEventFilter(self)
            app = QGuiApplication.instance()
            if isinstance(app, QGuiApplication):
                app.focusWindowChanged.disconnect(self._restore_renderer_focus_if_ready)
            self._focus_listener_connected = False
            self._focus_window = None

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Recheck a pending request after menu hiding or window activation."""
        if watched is self._menu and event.type() == QEvent.Type.Hide:
            if not self._focus_pending:
                self._request_renderer_focus()
            else:
                self._activate_owner_window()
                QTimer.singleShot(0, self._restore_renderer_focus_if_ready)
        elif self._focus_pending and watched is self._focus_window and event.type() == QEvent.Type.WindowActivate:
            QTimer.singleShot(0, self._restore_renderer_focus_if_ready)
        elif self._focus_pending and watched is self._focus_window and event.type() == QEvent.Type.Destroy:
            self._clear_focus_request()
        return super().eventFilter(watched, event)

    def _on_state_changed(self, path: str, value: object) -> None:
        """Synchronize the checked choice without invoking a command."""
        actions = self._actions.get(path)
        if actions is None:
            return
        for action_value, action in actions.items():
            action.setChecked(action_value == value)


class _ViewportCanvas(QWidget):
    """Own renderer layers and position private interactive viewport chrome."""

    def __init__(self, renderer: Renderer) -> None:
        super().__init__()
        self.view_control = _ViewControl(renderer, self)

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        """Keep the view control at the top-right of the viewport."""
        super().resizeEvent(event)
        hint = self.view_control.sizeHint()
        margin = 8
        self.view_control.setGeometry(max(margin, self.width() - hint.width() - margin), margin, hint.width(), hint.height())
        self.view_control.raise_()


class ViewPort(Component):
    """Combine the renderer and right sidebar in the main window.

    Parameters
    ----------
    window
        Main window that receives the viewport as its central widget.

    """

    def __init__(self, window: MainWindow) -> None:
        super().__init__()
        self.widget = QSplitter()
        self.renderer = Renderer()
        self._canvas = _ViewportCanvas(self.renderer)
        self._canvas_layout = QStackedLayout(self._canvas)
        self._canvas_layout.setContentsMargins(0, 0, 0, 0)
        self._canvas_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        self._canvas_layout.addWidget(self.renderer)
        self._overlay_canvas = _OverlayCanvas(self.renderer)
        self._canvas_layout.addWidget(self._overlay_canvas)
        self._canvas_layout.setCurrentWidget(self._overlay_canvas)
        self._view_control = self._canvas.view_control
        self._view_control.raise_()
        self.renderer.frameSwapped.connect(self.update_overlays)
        self.update_overlays()
        self.widget.addWidget(self._canvas)
        self.sidebar = SideBarRight(self)
        self.widget.addWidget(self.sidebar.widget)
        self.widget.setCollapsible(1, False)
        sidebar_width = self.viewer.config.ui.sidebar.width
        self.widget.setSizes([self.viewer.config.window.width - sidebar_width, sidebar_width])
        self.widget.setStretchFactor(0, 1)
        self.widget.setStretchFactor(1, 0)
        window.widget.setCentralWidget(self.widget)

    def update_overlays(self) -> None:
        """Synchronize and repaint transient screen overlays."""
        self._overlay_canvas.sync()
        self._view_control.raise_()
