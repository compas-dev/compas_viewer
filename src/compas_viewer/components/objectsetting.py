from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QVBoxLayout

from compas.colors import Color
from compas.colors import ColorDict
from compas.geometry import Box
from compas.geometry import Capsule
from compas.geometry import Cone
from compas.geometry import Cylinder
from compas.geometry import Sphere
from compas.geometry import Surface
from compas.geometry import Torus
from compas.scene import SceneItemNotBoundError
from compas.scene import SceneObject
from compas.scene import ShapeObject
from compas.scene import SurfaceObject
from compas_viewer.forms import scene_editable_attributes
from compas_viewer.scene.parameters import inspect_object_parameters

from .booleantoggle import BooleanToggle
from .colorpicker import ColorPicker
from .component import Component
from .container import Container
from .numberedit import NumberEdit
from .textedit import TextEdit

_BUFFER_SETTING_ATTRIBUTES = {
    "show",
    "show_points",
    "show_lines",
    "show_surfaces",
    "show_vertices",
    "show_edges",
    "show_nodes",
    "show_faces",
    "opacity",
    "pointsize",
    "vertexsize",
    "nodesize",
    "linewidth",
    "edgewidth",
}


@dataclass(slots=True)
class _EditableAttributeBinding:
    """Bind a control to one contextual stable scene-object attribute."""

    sceneobject: SceneObject
    name: str
    update: Callable[[SceneObject, object], None] | None

    @property
    def value(self) -> object:
        """Return the current attribute value."""
        return getattr(self.sceneobject, self.name)

    @value.setter
    def value(self, value: object) -> None:
        """Update the attribute and restore its prior value on failure."""
        previous = _snapshot_value(self.value)
        if self.integer_only and isinstance(value, float):
            if not value.is_integer():
                raise ValueError(f"Editable integer attribute {self.name} requires a whole number.")
            value = int(value)
        try:
            if self.update is None:
                setattr(self.sceneobject, self.name, value)
            else:
                self.update(self.sceneobject, value)
        except Exception:
            try:
                setattr(self.sceneobject, self.name, previous)
            except Exception:
                pass
            raise

    @property
    def integer_only(self) -> bool:
        """Whether the attribute's declared numeric contract requires integers."""
        for fields in self.sceneobject.scene_state_fields().values():
            for field in fields:
                if field.attribute != self.name:
                    continue
                accepted = field.value_type if isinstance(field.value_type, tuple) else (field.value_type,)
                if float in accepted:
                    return False
                if int in accepted:
                    return True
                break
        value = self.value
        return isinstance(value, int) and not isinstance(value, bool)


def _snapshot_value(value: object) -> object:
    """Copy mutable color mappings for transactional control rollback."""
    if isinstance(value, ColorDict):
        snapshot = ColorDict(value.default)
        snapshot.update(value)
        return snapshot
    return value


class ObjectSetting(Container):
    """Display editable properties for the current scene selection."""

    def __init__(self) -> None:
        super().__init__(container_type="scrollable", compact=True)

    @property
    def selected(self) -> list[SceneObject]:
        """list[SceneObject]: Currently selected stable scene objects."""
        return list(self.viewer.state.selection.objects)

    def update(self) -> None:
        """Update the layout with the latest object settings."""
        if len(self.selected) == 1:
            self.populate(self.selected[0])
        elif len(self.selected) > 1:
            self.reset()
            self.display_text(f"{len(self.selected)} objects selected")
            self._add_details_button(enabled=True)
        else:
            self.display_text("No object selected")
            self._add_details_button(enabled=False)

    def populate(self, obj: SceneObject) -> None:
        """Populate controls for a selected scene object.

        Parameters
        ----------
        obj
            Scene object whose editable properties should be displayed.

        """
        self.reset()
        controls = []
        for name, callback in self._editable_attributes(obj).items():
            control = self._create_control(_EditableAttributeBinding(obj, name, callback))
            if control is not None:
                controls.append(control)
        for control in controls:
            self.add(control)
        self._add_details_button(enabled=True)

    def _create_control(self, binding: _EditableAttributeBinding) -> Component | None:
        """Create a control inferred from the current attribute value."""
        value = binding.value
        titles = {"u": "U Resolution", "v": "V Resolution"}
        if isinstance(binding.sceneobject, (ShapeObject, SurfaceObject)):
            titles.update(
                {
                    "show_lines": "Show wireframe",
                    "linecolor": "Wireframe color",
                    "linewidth": "Wireframe width",
                }
            )
        title = titles.get(binding.name, binding.name.replace("_", " ").capitalize())

        def refresh(*args: object) -> None:
            self._refresh_object(binding.sceneobject, binding.name)

        if isinstance(value, bool):
            return BooleanToggle(binding, "value", title=title, action=refresh)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if binding.integer_only:
                control = NumberEdit(binding, "value", title=title, step=1.0, decimals=0, action=refresh)
                if binding.name in {"u", "v"}:
                    control.spinbox.setKeyboardTracking(False)
                return control
            return NumberEdit(binding, "value", title=title, action=refresh)
        if isinstance(value, str):
            return TextEdit(binding, "value", title=title, action=refresh)
        if isinstance(value, (Color, ColorDict)):
            return ColorPicker(binding, "value", title=title, action=refresh)
        return None

    def _refresh_object(self, sceneobject: SceneObject, attribute: str) -> None:
        """Refresh only the render state affected by one edited attribute."""
        if attribute == "name":
            self.viewer.ui.sidebar.sceneform.update(refresh=True)
            return

        render_object = self.scene.render_object(sceneobject)
        if attribute in {"u", "v"} and isinstance(sceneobject, (ShapeObject, SurfaceObject)):
            render_object.refresh_data()
            self.viewer.renderer.rebuild_buffers()
            self.viewer.ui.sidebar.sceneform.update(refresh=True)
        elif attribute in _BUFFER_SETTING_ATTRIBUTES:
            renderer = self.viewer.renderer
            if self.viewer.running:
                renderer.makeCurrent()
                try:
                    renderer.buffer_manager.update_object_settings(render_object)
                finally:
                    renderer.doneCurrent()
            if attribute == "show":
                self.viewer.ui.sidebar.sceneform.update(refresh=True)
        else:
            render_object.update(update_data=True)
        self.viewer.renderer.update()

    @staticmethod
    def _editable_attributes(obj: SceneObject) -> dict[str, Callable[[SceneObject, object], None] | None]:
        """Return the normalized Viewer attributes for the represented producer."""
        attributes = dict(scene_editable_attributes("Viewer", obj))
        if isinstance(obj, ShapeObject):
            try:
                item = obj.item
            except SceneItemNotBoundError:
                item = None
            if isinstance(item, Box) or not isinstance(item, (Cone, Cylinder, Capsule, Sphere, Torus)):
                attributes.pop("u", None)
            if not isinstance(item, (Capsule, Sphere, Torus)):
                attributes.pop("v", None)
        elif isinstance(obj, SurfaceObject):
            try:
                item = obj.item
            except SceneItemNotBoundError:
                item = None
            if not isinstance(item, Surface):
                attributes.pop("u", None)
                attributes.pop("v", None)
        return attributes

    def _item_type_name(self, sceneobject: SceneObject) -> str:
        """Return the represented type name without resolving external data."""
        try:
            item = sceneobject.item
        except SceneItemNotBoundError:
            return "Unresolved"
        return type(item).__name__ if item is not None else "Unresolved"

    def _add_details_button(self, *, enabled: bool) -> None:
        """Append the fixed selection-details action."""
        button = QPushButton("Details")
        button.setObjectName("objectDetailsButton")
        button.setEnabled(enabled)
        button.clicked.connect(self._show_details)
        assert self.layout is not None
        self.layout.addWidget(button)
        self.details_button = button

    def _show_details(self) -> None:
        """Show a read-only snapshot of the current scene selection."""
        selected = self.selected
        if not selected:
            return
        dialog = QDialog(self.viewer.ui.window.widget)
        dialog.setObjectName("objectDetailsDialog")
        dialog.setWindowTitle("Object Details")
        dialog.setModal(True)
        dialog.resize(520, 420)
        layout = QVBoxLayout(dialog)
        heading = QLabel("Selection snapshot")
        heading.setProperty("mutedText", True)
        layout.addWidget(heading)
        text = QPlainTextEdit()
        text.setObjectName("objectDetailsText")
        text.setReadOnly(True)
        text.setPlainText(self._details_text(selected))
        layout.addWidget(text)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.exec()

    def _details_text(self, selected: list[SceneObject]) -> str:
        """Return the complete read-only snapshot for a scene selection."""
        if len(selected) > 1:
            names = "\n".join(f"  {obj.name}" for obj in selected)
            types = ", ".join(sorted({self._item_type_name(obj) for obj in selected}))
            return f"{len(selected)} objects selected\nTypes: {types}\nNames:\n{names}"

        obj = selected[0]
        try:
            item = obj.item
        except SceneItemNotBoundError:
            item = None
        parameter_lines = []
        for name, parameter in inspect_object_parameters(item).items():
            value = repr(parameter.value) if parameter.available else "<not exposed by object>"
            parameter_lines.append(f"  {name}: {value}")
        parameters = "\nParameters:\n" + "\n".join(parameter_lines) if parameter_lines else ""
        item_type = type(item).__name__ if item is not None else "Unresolved"
        return f"Name: {obj.name}\nType: {item_type}\nVisible: {obj.show}{parameters}"
