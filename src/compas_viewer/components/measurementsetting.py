from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QSpinBox
from PySide6.QtWidgets import QWidget

from compas.tolerance import TOL

from .container import Container


class MeasurementSetting(Container):
    """Edit measurement presentation and report global COMPAS tolerance.

    Unit and precision are Viewer-owned presentation settings. The tolerance
    values come directly from the process-wide `compas.tolerance.TOL` object
    and are intentionally read-only.

    Notes
    -----
    This component does not convert coordinates, configure snapping, or mutate
    COMPAS tolerance.

    """

    def __init__(self) -> None:
        super().__init__(container_type="scrollable")

        contents = QWidget()
        form = QFormLayout(contents)

        self.unit_edit = QLineEdit()
        self.unit_edit.setObjectName("measurement_unit")
        self.unit_edit.setPlaceholderText("Unspecified")
        self.unit_edit.setToolTip("Coordinate-unit declaration for labels; coordinates are not converted.")
        self.unit_edit.setText(self.viewer.config.measurement.unit or "")
        self.unit_edit.editingFinished.connect(self._set_unit)
        form.addRow("Coordinate Unit", self.unit_edit)

        self.precision_edit = QSpinBox()
        self.precision_edit.setObjectName("measurement_precision")
        self.precision_edit.setRange(0, 2_147_483_647)
        self.precision_edit.setToolTip("Decimal places used to display measurements; this is not a geometry tolerance.")
        self.precision_edit.setValue(self.viewer.config.measurement.precision)
        self.precision_edit.valueChanged.connect(self._set_precision)
        form.addRow("Display Precision", self.precision_edit)

        self.tolerance_owner = QLabel("compas.tolerance.TOL (process-wide, read-only)")
        self.tolerance_owner.setWordWrap(True)
        self.tolerance_owner.setObjectName("measurement_tolerance_owner")
        form.addRow("Tolerance Owner", self.tolerance_owner)

        self.tolerance_labels: dict[str, QLabel] = {}
        for name, title in (
            ("unit", "Tolerance Unit"),
            ("absolute", "Absolute"),
            ("relative", "Relative"),
            ("angular", "Angular"),
            ("approximation", "Approximation"),
            ("precision", "Key Precision"),
            ("lineardeflection", "Linear Deflection"),
            ("angulardeflection", "Angular Deflection"),
        ):
            label = QLabel()
            label.setObjectName(f"measurement_tolerance_{name}")
            self.tolerance_labels[name] = label
            form.addRow(title, label)

        assert self.layout is not None
        self.layout.addWidget(contents)
        self._refresh_tolerance()
        self.viewer.state.changed.connect(self._on_state_changed)

    def update(self) -> None:
        """Refresh the displayed process-wide tolerance context."""
        self._refresh_tolerance()
        super().update()

    def _set_unit(self) -> None:
        unit = self.unit_edit.text().strip() or None
        self.viewer.state.set_measurement_unit(unit)
        self._sync_unit(unit)

    def _set_precision(self, precision: int) -> None:
        self.viewer.state.set_measurement_precision(precision)

    def _on_state_changed(self, path: str, value: object) -> None:
        if path == "measurement.unit":
            self._sync_unit(value if isinstance(value, str) else None)
        elif path == "measurement.precision" and isinstance(value, int):
            self.precision_edit.blockSignals(True)
            self.precision_edit.setValue(value)
            self.precision_edit.blockSignals(False)

    def _sync_unit(self, unit: str | None) -> None:
        self.unit_edit.blockSignals(True)
        self.unit_edit.setText(unit or "")
        self.unit_edit.blockSignals(False)

    def _refresh_tolerance(self) -> None:
        for name, label in self.tolerance_labels.items():
            label.setText(str(getattr(TOL, name)))


__all__ = ["MeasurementSetting"]
