from typing import TYPE_CHECKING


from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication

from compas_viewer.actions import Action
from compas_viewer.configurations import ControllerConfig

from .mouse import Mouse

if TYPE_CHECKING:
    from compas_viewer.components import Renderer
    from compas_viewer.viewer import Viewer


class Controller:
    """
    The Controller class is the main entry of all the key and mouse events.
    It is used to manage actions and events in the viewer.

    Parameters
    ----------
    viewer : :class:`compas_viewer.viewer.Viewer`
        The viewer object.
    config : :class:`compas_viewer.configurations.controller_config.ControllerConfig`
        The controller configuration.

    Attributes
    ----------
    viewer : :class:`compas_viewer.viewer.Viewer`
        The viewer object.
    config : :class:`compas_viewer.configurations.controller_config.ControllerConfig`
        The controller configuration.
    mouse : :class:`compas_viewer.controller.mouse.Mouse`
        The mouse object.
    """

    def __init__(self, viewer: "Viewer", config: ControllerConfig):
        self.viewer = viewer
        self.config = config
        self.mouse = Mouse()
        self.actions: dict[str, Action] = {}
        for k, v in self.config.actions.items():
            self.actions[k] = Action(k, self.viewer, v)

    # ==============================================================================
    # Actions
    # ==============================================================================

    def mouse_move_action(self, renderer: "Renderer", event: QMouseEvent):
        """
        The mouse move action of the renderer object.
        This function introduces elif for different actions, meaning only one action can be performed at a time.

        Parameters
        ----------
        renderer : :class:`compas_viewer.components.renderer.Renderer`
            The renderer object.
        event : :PySide6:`PySide6/QtGui/QMouseEvent`
            The Qt event.
        """

        # Record mouse position
        self.mouse.pos = event.pos()
        # Compute displacement
        dx = self.mouse.dx()
        dy = self.mouse.dy()

        # Drag selection
        if (
            event.buttons() == self.config.drag_selection.mouse
            and event.modifiers() == self.config.drag_selection.modifier
        ):
            renderer.selector.on_drag_selection = True
        # Drag deselection
        elif (
            event.buttons() == self.config.drag_deselection.mouse
            and event.modifiers() == self.config.drag_deselection.modifier
        ):
            renderer.selector.on_drag_selection = True
        # Pan
        elif event.buttons() == self.config.pan.mouse and event.modifiers() == self.config.pan.modifier:
            renderer.camera.pan(dx, dy)
        # Rotate
        elif event.buttons() == self.config.rotate.mouse and event.modifiers() == self.config.rotate.modifier:
            renderer.camera.rotate(dx, dy)

        # Record mouse position
        self.mouse.last_pos = event.pos()

    def mouse_press_action(self, renderer: "Renderer", event: QMouseEvent):
        """
        The mouse press action of the renderer object.
        This function introduces elif for different actions, meaning only one action can be performed at a time.

        Parameters
        ----------
        renderer : :class:`compas_viewer.components.renderer.Renderer`
            The renderer object.
        event : :PySide6:`PySide6/QtGui/QMouseEvent`
            The Qt event.
        """
        self.mouse.last_pos = event.pos()

        # Drag selection: not in the elif.
        if (
            event.buttons() == self.config.drag_selection.mouse
            and event.modifiers() == self.config.drag_selection.modifier
        ):
            renderer.selector.drag_start_pt = event.pos()
        # Drag deselection
        elif (
            event.buttons() == self.config.drag_deselection.mouse
            and event.modifiers() == self.config.drag_deselection.modifier
        ):
            renderer.selector.drag_start_pt = event.pos()

        # Select: single left click.
        if event.buttons() == Qt.MouseButton.LeftButton and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            renderer.selector.select.emit()
        # Multiselect
        elif event.buttons() == self.config.multiselect.mouse and event.modifiers() == self.config.multiselect.modifier:
            renderer.selector.multiselect.emit()
        # Deselect
        elif event.buttons() == self.config.deselect.mouse and event.modifiers() == self.config.deselect.modifier:
            renderer.selector.deselect.emit()
        # Pan
        elif (
            event.buttons() == self.config.pan.mouse
            and event.modifiers() == self.config.pan.modifier
            and event.modifiers() != self.config.rotate.modifier
        ):
            QApplication.setOverrideCursor(Qt.CursorShape.OpenHandCursor)
        # Rotate
        elif event.buttons() == self.config.rotate.mouse and event.modifiers() == self.config.rotate.modifier:
            QApplication.setOverrideCursor(Qt.CursorShape.SizeAllCursor)

        # Update the UI every time a mouse button is pressed.
        self.viewer.layout.update()

    def mouse_release_action(self, renderer: "Renderer", event: QMouseEvent):
        """
        The mouse release action of the renderer object.
        This function introduces elif for different actions, meaning only one action can be performed at a time.

        Parameters
        ----------
        renderer : :class:`compas_viewer.components.renderer.Renderer`
            The renderer object.
        event : :PySide6:`PySide6/QtGui/QMouseEvent`
            The Qt event.
        """

        # Drag selection
        if event.modifiers() == self.config.drag_selection.modifier and renderer.selector.on_drag_selection:
            renderer.selector.on_drag_selection = False
            renderer.selector.drag_end_pt = event.pos()
            renderer.selector.drag_selection.emit()
        # Drag deselection
        elif event.modifiers() == self.config.drag_deselection.modifier and renderer.selector.on_drag_selection:
            renderer.selector.on_drag_selection = False
            renderer.selector.drag_end_pt = event.pos()
            renderer.selector.drag_deselection.emit()

        if event.buttons() == Qt.KeyboardModifier.NoModifier or event.buttons() == Qt.MouseButton.NoButton:
            QApplication.restoreOverrideCursor()

    def wheel_action(self, renderer: "Renderer", event: QWheelEvent):
        """
        The wheel action of the renderer object.
        It is used from zooming action only.

        Parameters
        ----------
        renderer : :class:`compas_viewer.components.renderer.Renderer`
            The renderer object.
        event : :PySide6:`PySide6/QtGui/QWheelEvent`
            The Qt event.
        """
        degrees = event.angleDelta().y() / 8
        steps = degrees / 15
        renderer.camera.zoom(int(steps))

    def key_press_action(self, renderer: "Renderer", event: QKeyEvent):
        """
        The key press action of the renderer object.
        This function introduces break for different actions, meaning only one action can be performed at a time.

        Parameters
        ----------
        renderer : :class:`compas_viewer.components.renderer.Renderer`
            The renderer object.
        event : :PySide6:`PySide6/QtGui/QKeyEvent`
            The Qt event.
        """
        for action in self.actions.values():
            if event.key() == action.key and event.modifiers() == action.modifier:
                action.pressed.emit()
                break

    def key_release_action(self, renderer: "Renderer", event: QKeyEvent):
        """
        The key release action of the renderer object.
        This function introduces break for different actions, meaning only one action can be performed at a time.

        Parameters
        ----------
        renderer : :class:`compas_viewer.components.renderer.Renderer`
            The renderer object.
        event : :PySide6:`PySide6/QtGui/QKeyEvent`
            The Qt event.
        """
        for action in self.actions.values():
            if event.key() == action.key and event.modifiers() == action.modifier:
                action.released.emit()
                break
