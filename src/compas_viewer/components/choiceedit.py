from collections.abc import Callable
from collections.abc import Sequence

from PySide6.QtWidgets import QComboBox
from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QWidget

from .boundcomponent import BoundComponent
from .component import Component


class ChoiceEdit(BoundComponent[str]):
    """Create a labeled choice box bound to a string attribute.

    Parameters
    ----------
    obj
        Object or dictionary containing the edited value.
    attr
        Attribute or key to edit.
    choices
        Available string values.
    title
        Optional label shown beside the choice box.
    action
        Optional callback invoked after a choice is applied.

    """

    def __init__(
        self,
        obj: object | dict[str, str],
        attr: str,
        choices: Sequence[str],
        title: str | None = None,
        action: Callable[[Component, str], None] | None = None,
    ) -> None:
        super().__init__(obj, attr, action=action)
        self.widget = QWidget()
        self.layout = QHBoxLayout()
        self.label = QLabel(title or attr)
        self.combobox = QComboBox()
        self.combobox.addItems(choices)
        self.combobox.setCurrentText(str(self.get_attr()))
        self.combobox.setMaximumSize(110, 25)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)
        self.widget.setLayout(self.layout)
        self.combobox.currentTextChanged.connect(self.on_value_changed)

    def sync_from_bound_object(self, value: str) -> None:
        """Synchronize the choice box with its bound value."""
        self.combobox.blockSignals(True)
        self.combobox.setCurrentText(value)
        self.combobox.blockSignals(False)
