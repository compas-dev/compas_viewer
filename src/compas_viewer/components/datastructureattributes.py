from collections.abc import Callable
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import QPersistentModelIndex
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QWidget

from compas.scene import SceneItemNotBoundError
from compas.scene import SceneObject

from .container import Container


@dataclass(frozen=True, slots=True)
class _ElementDomain:
    """Adapt one established datastructure element-attribute domain."""

    item: object
    name: str
    title: str
    defaults_name: str
    keys_name: str
    attribute_name: str
    unset_name: str

    @property
    def defaults(self) -> Mapping[str, object]:
        """Return the ordered default attributes defining table columns."""
        return cast(Mapping[str, object], getattr(self.item, self.defaults_name))

    def keys(self) -> tuple[object, ...]:
        """Snapshot element keys in datastructure iteration order."""
        return tuple(getattr(self.item, self.keys_name)())

    def value(self, key: object, name: str) -> object:
        """Return one effective element attribute value."""
        return getattr(self.item, self.attribute_name)(key, name)

    def set_value(self, key: object, name: str, value: object) -> None:
        """Set one explicit element attribute value."""
        getattr(self.item, self.attribute_name)(key, name, value)

    def unset_value(self, key: object, name: str) -> None:
        """Remove one override so the declared default becomes effective."""
        getattr(self.item, self.unset_name)(key, name)


_DOMAIN_SPECS = (
    ("nodes", "Nodes", "default_node_attributes", "nodes", "node_attribute", "unset_node_attribute"),
    ("vertices", "Vertices", "default_vertex_attributes", "vertices", "vertex_attribute", "unset_vertex_attribute"),
    ("edges", "Edges", "default_edge_attributes", "edges", "edge_attribute", "unset_edge_attribute"),
    ("faces", "Faces", "default_face_attributes", "faces", "face_attribute", "unset_face_attribute"),
)


def _element_domains(item: object) -> tuple[_ElementDomain, ...]:
    """Discover declared Mesh or Graph element-attribute domains."""
    from compas.datastructures import Graph
    from compas.datastructures import Mesh

    if not isinstance(item, (Mesh, Graph)):
        return ()

    domains: list[_ElementDomain] = []
    for name, title, defaults_name, keys_name, attribute_name, unset_name in _DOMAIN_SPECS:
        defaults = getattr(item, defaults_name, None)
        keys = getattr(item, keys_name, None)
        attribute = getattr(item, attribute_name, None)
        unset = getattr(item, unset_name, None)
        if not isinstance(defaults, Mapping) or not defaults:
            continue
        if not callable(keys) or not callable(attribute) or not callable(unset):
            continue
        domains.append(
            _ElementDomain(
                item=item,
                name=name,
                title=title,
                defaults_name=defaults_name,
                keys_name=keys_name,
                attribute_name=attribute_name,
                unset_name=unset_name,
            )
        )
    return tuple(domains)


def _editable_type(value: object) -> type[bool] | type[int] | type[float] | type[str] | None:
    """Return the supported scalar editor type selected by a default value."""
    if isinstance(value, bool):
        return bool
    if isinstance(value, int):
        return int
    if isinstance(value, float):
        return float
    if isinstance(value, str):
        return str
    return None


class _ElementAttributesModel(QAbstractTableModel):
    """Fetch and mutate one element-attribute domain lazily."""

    def __init__(
        self,
        domain: _ElementDomain,
        *,
        changed: Callable[[], None],
        failed: Callable[[Exception], None],
    ) -> None:
        super().__init__()
        self.domain = domain
        self.keys = domain.keys()
        self.attributes = tuple(domain.defaults)
        self._changed = changed
        self._failed = failed

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        """Return the number of snapshotted element keys."""
        return 0 if parent.isValid() else len(self.keys)

    def columnCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()) -> int:
        """Return the element-key column plus declared attribute columns."""
        return 0 if parent.isValid() else len(self.attributes) + 1

    def data(self, index: QModelIndex | QPersistentModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        """Return a display, edit, or check-state value for one cell."""
        if not index.isValid():
            return None
        key = self.keys[index.row()]
        if index.column() == 0:
            if role == Qt.ItemDataRole.DisplayRole:
                return self._display_key(key)
            return None

        name = self.attributes[index.column() - 1]
        value = self.domain.value(key, name)
        if role == Qt.ItemDataRole.CheckStateRole and isinstance(value, bool):
            return Qt.CheckState.Checked if value else Qt.CheckState.Unchecked
        if role == Qt.ItemDataRole.DisplayRole:
            return "" if isinstance(value, bool) else str(value)
        if role == Qt.ItemDataRole.EditRole:
            return value
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> object | None:
        """Return horizontal column names and one-based vertical row numbers."""
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return "Key" if section == 0 else self.attributes[section - 1]
        return str(section + 1)

    def flags(self, index: QModelIndex | QPersistentModelIndex) -> Qt.ItemFlag:
        """Return edit flags derived from the declared default value type."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if index.column() == 0:
            return flags
        default = self.domain.defaults[self.attributes[index.column() - 1]]
        value_type = _editable_type(default)
        if value_type is None:
            return flags
        flags |= Qt.ItemFlag.ItemIsEditable
        if value_type is bool:
            flags |= Qt.ItemFlag.ItemIsUserCheckable
        return flags

    def setData(self, index: QModelIndex | QPersistentModelIndex, value: object, role: int = Qt.ItemDataRole.EditRole) -> bool:
        """Commit one scalar cell through the singular datastructure setter."""
        if not index.isValid() or index.column() == 0:
            return False
        if role not in {Qt.ItemDataRole.EditRole, Qt.ItemDataRole.CheckStateRole}:
            return False

        name = self.attributes[index.column() - 1]
        value_type = _editable_type(self.domain.defaults[name])
        if value_type is None:
            return False
        try:
            converted = self._convert(value, value_type, role)
            self.domain.set_value(self.keys[index.row()], name, converted)
        except Exception as error:
            self._notify_cell(index)
            self._failed(error)
            return False

        self._notify_cell(index)
        self._changed()
        return True

    def reset_to_default(self, index: QModelIndex, *, refresh: bool = True) -> bool:
        """Remove one editable cell override through the singular unsetter."""
        if not index.isValid() or index.column() == 0:
            return False
        name = self.attributes[index.column() - 1]
        if _editable_type(self.domain.defaults[name]) is None:
            return False
        try:
            self.domain.unset_value(self.keys[index.row()], name)
        except Exception as error:
            self._notify_cell(index)
            self._failed(error)
            return False

        self._notify_cell(index)
        if refresh:
            self._changed()
        return True

    def _convert(
        self,
        value: object,
        value_type: type[bool] | type[int] | type[float] | type[str],
        role: int,
    ) -> bool | int | float | str:
        if value_type is bool:
            if role == Qt.ItemDataRole.CheckStateRole:
                if value == Qt.CheckState.Checked or value == Qt.CheckState.Checked.value:
                    return True
                if value == Qt.CheckState.Unchecked or value == Qt.CheckState.Unchecked.value:
                    return False
                raise TypeError(f"{self.domain.name} attribute requires a checked or unchecked state.")
            if isinstance(value, bool):
                return value
        elif value_type is int:
            if isinstance(value, int) and not isinstance(value, bool):
                return value
        elif value_type is float:
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
        elif isinstance(value, str):
            return value
        raise TypeError(f"{self.domain.name} attribute requires a {value_type.__name__} value.")

    def _notify_cell(self, index: QModelIndex | QPersistentModelIndex) -> None:
        self.dataChanged.emit(
            index,
            index,
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole, Qt.ItemDataRole.CheckStateRole],
        )

    def _display_key(self, key: object) -> str:
        return repr(key) if self.domain.name == "edges" else str(key)


class DatastructureAttributes(Container):
    """Display editable element attributes for one selected Mesh or Graph.

    The table columns come from the datastructure's ordered default-attribute
    dictionaries. Values are read lazily through singular element accessors,
    and successful mutations conservatively rebuild the selected object's
    Viewer render data.

    """

    def __init__(self) -> None:
        super().__init__()
        assert self.layout is not None
        self.message = QLabel()
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabs = QTabWidget()
        self.reset_button = QPushButton("Reset to default")
        self.reset_button.clicked.connect(self.reset_selected)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.reset_button)
        self._sceneobject: SceneObject | None = None
        self._tables: dict[QWidget, QTableView] = {}
        self._show_message("Select one Mesh or Graph")

    @property
    def selected(self) -> list[SceneObject]:
        """list[SceneObject]: Currently selected stable scene objects."""
        return [sceneobject for sceneobject in self.scene.objects if self.scene.is_selected(sceneobject)]

    def update(self) -> None:
        """Rebuild attribute tabs for the current single selection."""
        if len(self.selected) != 1:
            self._show_message("Select one Mesh or Graph")
            return
        sceneobject = self.selected[0]
        try:
            item = sceneobject.item
        except SceneItemNotBoundError:
            self._show_message("The selected data is not bound")
            return
        if item is None:
            self._show_message("The selected scene object has no data")
            return

        domains = _element_domains(item)
        if not domains:
            self._show_message("No declared element attributes")
            return
        self._populate(sceneobject, domains)

    def reset_selected(self) -> None:
        """Reset selected editable cells to their declared defaults."""
        table = self._current_table()
        if table is None:
            return
        model = cast(_ElementAttributesModel, table.model())
        selection = table.selectionModel()
        if selection is None:
            return
        changed = False
        for index in selection.selectedIndexes():
            changed = model.reset_to_default(index, refresh=False) or changed
        if changed and self._sceneobject is not None:
            self._refresh_object(self._sceneobject)

    def _populate(self, sceneobject: SceneObject, domains: tuple[_ElementDomain, ...]) -> None:
        self.tabs.clear()
        self._tables = {}
        self._sceneobject = sceneobject
        for domain in domains:
            table = QTableView()
            model = _ElementAttributesModel(
                domain,
                changed=lambda sceneobject=sceneobject: self._refresh_object(sceneobject),
                failed=self._report_error,
            )
            table.setModel(model)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
            table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
            table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)
            table.setAlternatingRowColors(True)
            self.tabs.addTab(table, domain.title)
            self._tables[table] = table
        self.message.hide()
        self.tabs.show()
        self.reset_button.setEnabled(True)
        self.reset_button.show()

    def _show_message(self, text: str) -> None:
        self.tabs.clear()
        self._tables = {}
        self._sceneobject = None
        self.message.setText(text)
        self.message.show()
        self.tabs.hide()
        self.reset_button.setEnabled(False)
        self.reset_button.hide()

    def _current_table(self) -> QTableView | None:
        widget = self.tabs.currentWidget()
        return self._tables.get(widget) if widget is not None else None

    def _refresh_object(self, sceneobject: SceneObject) -> None:
        render_object = self.scene.render_object(sceneobject)
        render_object.refresh_data()
        render_object.update(update_data=True)
        self.viewer.renderer.update()
        sidebar = self.viewer.ui.sidebar
        if hasattr(sidebar, "sceneform"):
            sidebar.sceneform.update(refresh=True)
        if hasattr(sidebar, "object_setting"):
            sidebar.object_setting.update()

    def _report_error(self, error: Exception) -> None:
        QMessageBox.critical(self.widget, "Could Not Update Attribute", str(error))


__all__ = ["DatastructureAttributes"]
