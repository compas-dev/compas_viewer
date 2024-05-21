from dataclasses import asdict

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QPinchGesture

from compas_viewer.actions import Action
from compas_viewer.base import Base
from compas_viewer.config import Config
from compas_viewer.qt import key_mapper

from .mouse import Mouse


class ActionConfig:
    """
    The class representation  of the key-based action configuration.
    The action config contains two elements, "key" and "modifier".

    Parameters
    ----------
    key : str
        The key.
    modifier : str, optional
        The key modifier.

    Attributes
    ----------
    config : :class:`ActionConfigType`
        A TypedDict with defined keys and types.
    key : :QtCore:`PySide6.QtCore.Qt.Key`
        The Qt key.
    modifier : :QtCore:`PySide6.QtCore.Qt.KeyboardModifier`
        The Qt modifier.

    See Also
    --------
    :class:`compas_viewer.configurations.controller_config.ControllerConfig`
    """

    def __init__(self, key: str, modifier: str = "no"):
        self.key = key_mapper(key, 0)
        self.modifier = key_mapper(modifier, 1)


class Controller(Base):
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

    def __init__(self, config: Config):
        self.config = config
        self.mouse = Mouse()

        self.mouse_actions: dict[str, Action] = {}
        for name, value in asdict(self.config.mouse_event).items():
            self.mouse_actions[name] = {"mouse": key_mapper(value["mouse"], 2), "modifier": key_mapper(value["modifier"], 1)}

        self.key_actions: dict[str, Action] = {}
        for name in asdict(self.config.key_event):
            value = getattr(self.config.key_event, name)
            self.key_actions[name] = Action(name, ActionConfig(value.key, value.modifier))

    # ==============================================================================
    # Actions
    # ==============================================================================

    def mouse_move_action(self, event: QMouseEvent):
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
        if event.buttons() == self.mouse_actions["drag_selection"]["mouse"] and event.modifiers() == self.mouse_actions["drag_selection"]["modifier"]:
            self.viewer.renderer.selector.on_drag_selection = True

        # Drag deselection
        elif event.buttons() == self.mouse_actions["drag_deselection"]["mouse"] and event.modifiers() == self.mouse_actions["drag_deselection"]["modifier"]:
            self.viewer.renderer.selector.on_drag_selection = True

        # Pan
        elif event.buttons() == self.mouse_actions["pan"]["mouse"] and event.modifiers() == self.mouse_actions["pan"]["modifier"]:
            self.viewer.renderer.camera.pan(dx, dy)

        # Rotate
        elif event.buttons() == self.mouse_actions["rotate"]["mouse"] and event.modifiers() == self.mouse_actions["rotate"]["modifier"]:
            self.viewer.renderer.camera.rotate(dx, dy)

        # Record mouse position
        self.mouse.last_pos = event.pos()

    def mouse_press_action(self, event: QMouseEvent):
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

        # Drag selection
        if event.buttons() == self.mouse_actions["drag_selection"]["mouse"] and event.modifiers() == self.mouse_actions["drag_selection"]["modifier"]:
            self.viewer.renderer.selector.drag_start_pt = event.pos()

        # Drag deselection
        elif event.buttons() == self.mouse_actions["drag_deselection"]["mouse"] and event.modifiers() == self.mouse_actions["drag_deselection"]["modifier"]:
            self.viewer.renderer.selector.drag_start_pt = event.pos()

        # Select: single left click.
        if event.buttons() == Qt.MouseButton.LeftButton and event.modifiers() == Qt.KeyboardModifier.NoModifier:
            self.viewer.renderer.selector.select.emit()

        # Multiselect
        elif event.buttons() == self.mouse_actions["multiselect"]["mouse"] and event.modifiers() == self.mouse_actions["multiselect"]["modifier"]:
            self.viewer.renderer.selector.multiselect.emit()

        # Deselect
        elif event.buttons() == self.mouse_actions["deselect"]["mouse"] and event.modifiers() == self.mouse_actions["deselect"]["modifier"]:
            self.viewer.renderer.selector.deselect.emit()

        # Pan
        elif (
            event.buttons() == self.mouse_actions["pan"]["mouse"]
            and event.modifiers() == self.mouse_actions["pan"]["modifier"]
            and event.modifiers() != self.mouse_actions["rotate"]["modifier"]
        ):
            QApplication.setOverrideCursor(Qt.CursorShape.OpenHandCursor)

        # Rotate
        elif event.buttons() == self.mouse_actions["rotate"]["mouse"] and event.modifiers() == self.mouse_actions["rotate"]["modifier"]:
            QApplication.setOverrideCursor(Qt.CursorShape.SizeAllCursor)

    def mouse_release_action(self, event: QMouseEvent):
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
        if event.modifiers() == self.mouse_actions["drag_selection"]["modifier"] and self.viewer.renderer.selector.on_drag_selection:
            self.viewer.renderer.selector.on_drag_selection = False
            self.viewer.renderer.selector.drag_end_pt = event.pos()
            self.viewer.renderer.selector.drag_selection.emit()
        # Drag deselection
        elif event.modifiers() == self.mouse_actions["drag_selection"]["modifier"] and self.viewer.renderer.selector.on_drag_selection:
            self.viewer.renderer.selector.on_drag_selection = False
            self.viewer.renderer.selector.drag_end_pt = event.pos()
            self.viewer.renderer.selector.drag_deselection.emit()

        if event.buttons() == Qt.KeyboardModifier.NoModifier or event.buttons() == Qt.MouseButton.NoButton:
            QApplication.restoreOverrideCursor()

    def pinch_action(self, event: QPinchGesture):
        """
        The pinch action of the renderer object.

        Parameters
        ----------
        renderer : :class:`compas_viewer.components.renderer.Renderer`
            The renderer object.
        event : :PySide6:`PySide6/QtWidgets/QPinchGesture`
            The Qt event.

        """
        steps = event.scaleFactor() - 1
        steps *= 10
        self.viewer.renderer.camera.zoom(steps)

    def wheel_action(self, event: QWheelEvent):
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
        self.viewer.renderer.camera.zoom(steps)

    def key_press_action(self, event: QKeyEvent):
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
        for action in self.key_actions.values():
            if event.key() == action.key and event.modifiers() == action.modifier:
                action.pressed.emit()
                break

    def key_release_action(self, event: QKeyEvent):
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
        for action in self.key_actions.values():
            if event.key() == action.key and event.modifiers() == action.modifier:
                action.released.emit()
                break
