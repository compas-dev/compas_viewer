from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QSpinBox
from PySide6.QtWidgets import QWidget

from .booleantoggle import BooleanToggle
from .boundcomponent import BoundComponent
from .choiceedit import ChoiceEdit
from .colorpicker import ColorPicker
from .component import Component
from .container import Container
from .numberedit import NumberEdit


class _FieldRow(Component):
    """Place one editor beside its System-section label."""

    def __init__(self, title: str, field: QWidget) -> None:
        super().__init__()
        self.widget = QWidget()
        self.layout = QHBoxLayout(self.widget)
        self.label = QLabel(title)
        self.field = field
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.field)


class GridUnitSetting(Container):
    """Edit grid display and measurement-presentation settings.

    Coordinate units are informational. Changing the unit does not convert
    geometry, grid spacing, snapping, measurements, or COMPAS tolerance.

    """

    def __init__(self) -> None:
        super().__init__(container_type="scrollable", compact=True)
        renderer_config = self.viewer.config.renderer
        dx, nx, dy, ny = renderer_config.gridsize
        self.grid = SimpleNamespace(dx=dx, nx=float(nx), dy=dy, ny=float(ny))
        self._state_controls: dict[str, BoundComponent[Any]] = {}

        def notify(path: str) -> Callable[..., None]:
            def publish(*args: object) -> None:
                self.viewer.state.notify(path)

            return publish

        def update_grid(*args: object) -> None:
            self.viewer.state.set("renderer.gridsize", (self.grid.dx, int(self.grid.nx), self.grid.dy, int(self.grid.ny)))

        def add_state_control(path: str, control: BoundComponent[Any]) -> None:
            self._state_controls[path] = control
            self.add(control)

        add_state_control("renderer.show_grid", BooleanToggle(renderer_config, "show_grid", title="Show Grid", action=notify("renderer.show_grid")))
        add_state_control("renderer.show_gridz", BooleanToggle(renderer_config, "show_gridz", title="Show Z Axis", action=notify("renderer.show_gridz")))
        add_state_control("renderer.gridmode", ChoiceEdit(renderer_config, "gridmode", ["full", "quadrant"], title="Grid Mode", action=notify("renderer.gridmode")))
        add_state_control("renderer.gridcolor", ColorPicker(renderer_config, "gridcolor", title="Grid Color", action=notify("renderer.gridcolor")))
        self.add(NumberEdit(self.grid, "dx", title="Grid X Extent", min_val=0.001, max_val=1e9, action=update_grid))
        self.add(NumberEdit(self.grid, "nx", title="Grid X Divisions", min_val=1, max_val=1000, step=1, decimals=0, action=update_grid))
        self.add(NumberEdit(self.grid, "dy", title="Grid Y Extent", min_val=0.001, max_val=1e9, action=update_grid))
        self.add(NumberEdit(self.grid, "ny", title="Grid Y Divisions", min_val=1, max_val=1000, step=1, decimals=0, action=update_grid))

        self.unit_edit = QLineEdit()
        self.unit_edit.setObjectName("measurement_unit")
        self.unit_edit.setPlaceholderText("Unspecified")
        self.unit_edit.setToolTip("Coordinate-unit declaration for labels; coordinates are not converted.")
        self.unit_edit.setText(self.viewer.config.measurement.unit or "")
        self.unit_edit.editingFinished.connect(self._set_unit)
        self.add(_FieldRow("Coordinate Unit", self.unit_edit))

        self.precision_edit = QSpinBox()
        self.precision_edit.setObjectName("measurement_precision")
        self.precision_edit.setRange(0, 2_147_483_647)
        self.precision_edit.setToolTip("Decimal places used to display measurements; this is not a geometry tolerance.")
        self.precision_edit.setValue(self.viewer.config.measurement.precision)
        self.precision_edit.valueChanged.connect(self._set_precision)
        self.add(_FieldRow("Display Precision", self.precision_edit))

        self.viewer.state.changed.connect(self._on_state_changed)

    def _set_unit(self) -> None:
        unit = self.unit_edit.text().strip() or None
        self.viewer.state.set_measurement_unit(unit)
        self._sync_unit(unit)

    def _set_precision(self, precision: int) -> None:
        self.viewer.state.set_measurement_precision(precision)

    def _on_state_changed(self, path: str, value: object) -> None:
        if path == "renderer.gridsize":
            dx, nx, dy, ny = self.viewer.config.renderer.gridsize
            self.grid.dx = dx
            self.grid.nx = float(nx)
            self.grid.dy = dy
            self.grid.ny = float(ny)
        elif control := self._state_controls.get(path):
            control.sync_from_bound_object(value)
        elif path == "measurement.unit":
            self._sync_unit(value if isinstance(value, str) else None)
        elif path == "measurement.precision" and isinstance(value, int):
            self.precision_edit.blockSignals(True)
            self.precision_edit.setValue(value)
            self.precision_edit.blockSignals(False)

    def _sync_unit(self, unit: str | None) -> None:
        self.unit_edit.blockSignals(True)
        self.unit_edit.setText(unit or "")
        self.unit_edit.blockSignals(False)


__all__ = ["GridUnitSetting"]
