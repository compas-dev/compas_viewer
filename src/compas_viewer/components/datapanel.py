from dataclasses import dataclass
from uuid import UUID

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFormLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from compas.data import Data
from compas.scene import Scene
from compas_viewer.scene.parameters import inspect_object_parameters

from .component import Component
from .datastructureattributes import _element_domains
from .datastructureattributes import _ElementAttributesModel


@dataclass(frozen=True, slots=True)
class _DataReference:
    domain: str
    guid: UUID
    name: str


@dataclass(frozen=True, slots=True)
class _DataInventoryItem:
    guid: UUID
    item: Data | None
    references: tuple[_DataReference, ...]

    @property
    def name(self) -> str:
        if self.item is not None and self.item.name:
            return self.item.name
        return self.references[0].name

    @property
    def type_name(self) -> str:
        return type(self.item).__name__ if self.item is not None else "Unknown"


def _data_inventory(scene: Scene) -> tuple[_DataInventoryItem, ...]:
    """Project the active scene's distinct item references in stable order."""
    references: dict[UUID, list[_DataReference]] = {}
    for sceneobject in scene.objects:
        guid = sceneobject.item_guid
        if guid is not None:
            references.setdefault(guid, []).append(_DataReference("Scene", sceneobject.guid, sceneobject.name))
    for annotation in scene.annotations:
        references.setdefault(annotation.item_guid, []).append(_DataReference("Annotation", annotation.guid, annotation.name))
    return tuple(_DataInventoryItem(guid, scene.item_store.get(guid), tuple(referrers)) for guid, referrers in references.items())


def _safe_parameters(item: Data) -> tuple[tuple[str, object], ...]:
    """Read public constructor attributes without accessing ``__data__``."""
    return tuple((name, parameter.value) for name, parameter in inspect_object_parameters(item, use_serialized_fallback=False).items() if parameter.available)


def _display_value(value: object) -> str:
    """Format one inspected value without allowing a hostile formatter to escape."""
    try:
        return str(value)
    except Exception as error:
        return f"<unavailable: {type(error).__name__}>"


class DataDetailsDialog(QDialog):
    """Show a read-only snapshot of one referenced data item."""

    def __init__(self, record: _DataInventoryItem, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Data Details")
        self.setModal(True)
        self.resize(720, 520)
        layout = QVBoxLayout(self)
        metadata = QFormLayout()
        metadata.addRow("Name", QLabel(record.name))
        metadata.addRow("Type", QLabel(record.type_name))
        metadata.addRow("GUID", QLabel(str(record.guid)))
        metadata.addRow("Status", QLabel("Bound" if record.item is not None else "Unresolved"))
        metadata.addRow("References", QLabel("\n".join(f"{ref.domain}: {ref.name} ({ref.guid})" for ref in record.references)))
        layout.addLayout(metadata)

        if record.item is not None:
            domains = _element_domains(record.item)
            if domains:
                tabs = QTabWidget()
                for domain in domains:
                    table = QTableView()
                    table.setModel(_ElementAttributesModel(domain, changed=lambda: None, failed=lambda _error: None, editable=False))
                    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                    table.setAlternatingRowColors(True)
                    tabs.addTab(table, domain.title)
                layout.addWidget(tabs)
            else:
                parameters = QTableWidget(0, 2)
                parameters.setHorizontalHeaderLabels(["Parameter", "Value"])
                parameters.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
                for name, value in _safe_parameters(record.item):
                    row = parameters.rowCount()
                    parameters.insertRow(row)
                    parameters.setItem(row, 0, QTableWidgetItem(name))
                    parameters.setItem(row, 1, QTableWidgetItem(_display_value(value)))
                layout.addWidget(parameters)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class DataPanel(Component):
    """Display the active scene's referenced data as a flat read-only list."""

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Status", "References"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._update_details_enabled)
        self.table.itemDoubleClicked.connect(lambda _item: self.show_details())
        self.details_button = QPushButton("Details")
        self.details_button.setEnabled(False)
        self.details_button.clicked.connect(self.show_details)
        layout.addWidget(self.table)
        layout.addWidget(self.details_button)
        self._records: dict[UUID, _DataInventoryItem] = {}

    @property
    def selected_guid(self) -> UUID | None:
        """Return the locally selected referenced-item GUID."""
        rows = self.table.selectionModel().selectedRows() if self.table.selectionModel() is not None else []
        return rows[0].data(Qt.ItemDataRole.UserRole) if rows else None

    def update(self) -> None:
        """Rebuild the projection while preserving a still-referenced selection."""
        selected = self.selected_guid
        inventory = _data_inventory(self.scene)
        self._records = {record.guid: record for record in inventory}
        self.table.setRowCount(len(inventory))
        for row, record in enumerate(inventory):
            values = (record.name, record.type_name, "Bound" if record.item is not None else "Unresolved", str(len(record.references)))
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, record.guid)
                self.table.setItem(row, column, item)
            if record.guid == selected:
                self.table.selectRow(row)
        self._update_details_enabled()

    def show_details(self) -> None:
        """Open a main-window-owned modal details snapshot for the selected row."""
        guid = self.selected_guid
        if guid is None:
            return
        dialog = DataDetailsDialog(self._records[guid], self.viewer.ui.window.widget)
        dialog.exec()

    def _update_details_enabled(self) -> None:
        self.details_button.setEnabled(self.selected_guid is not None)


__all__ = ["DataDetailsDialog", "DataPanel"]
