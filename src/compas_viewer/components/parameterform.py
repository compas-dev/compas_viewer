from typing import Any

from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QDoubleSpinBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QScrollArea
from PySide6.QtWidgets import QSpinBox
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas_viewer.scene.parameters import inspect_object_parameters


class ParameterForm(QDialog):
    """Edit writable scalar parameters of an object's underlying data.

    Parameters
    ----------
    obj
        Data object whose constructor parameters should be presented.
    title
        Optional dialog title.
    parent
        Optional parent widget.

    """

    def __init__(self, obj: object, title: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title or f"Modify {type(obj).__name__}")
        self.setMinimumWidth(360)
        self._editors: dict[str, QCheckBox | QDoubleSpinBox | QLineEdit | QSpinBox] = {}

        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contents = QWidget()
        form = QFormLayout(contents)

        for name, parameter in inspect_object_parameters(obj).items():
            if not parameter.available or not parameter.writable:
                continue
            editor = self._make_editor(name, parameter.value)
            if editor is None:
                continue
            self._editors[name] = editor
            form.addRow(name.replace("_", " ").title(), editor)

        if not self._editors:
            form.addRow(QLabel("This object has no editable scalar parameters."))

        scroll.setWidget(contents)
        layout.addWidget(scroll)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _make_editor(name: str, value: Any) -> QCheckBox | QDoubleSpinBox | QLineEdit | QSpinBox | None:
        if isinstance(value, bool):
            editor = QCheckBox()
            editor.setChecked(value)
        elif isinstance(value, int):
            editor = QSpinBox()
            editor.setRange(-2_147_483_648, 2_147_483_647)
            editor.setValue(value)
        elif isinstance(value, float):
            editor = QDoubleSpinBox()
            editor.setDecimals(8)
            editor.setRange(-1.0e12, 1.0e12)
            editor.setSingleStep(0.1)
            editor.setValue(value)
        elif isinstance(value, str):
            editor = QLineEdit(value)
        else:
            return None
        editor.setObjectName(f"parameter_{name}")
        return editor

    def values(self) -> dict[str, bool | float | int | str]:
        """Return the values currently entered in the form.

        Returns
        -------
        dict[str, bool | float | int | str]
            Edited values keyed by parameter name.

        """
        values: dict[str, bool | float | int | str] = {}
        for name, editor in self._editors.items():
            if isinstance(editor, QCheckBox):
                values[name] = editor.isChecked()
            elif isinstance(editor, QSpinBox):
                values[name] = editor.value()
            elif isinstance(editor, QDoubleSpinBox):
                values[name] = editor.value()
            else:
                values[name] = editor.text()
        return values
