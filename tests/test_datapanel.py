from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTableView

from compas.data import Data
from compas.datastructures import Mesh
from compas.geometry import Sphere
from compas.scene import SceneAnnotation
from compas.scene import SceneObject
from compas.scene import TextAnnotation
from compas_viewer import Viewer
from compas_viewer.base import Base
from compas_viewer.components.datapanel import DataDetailsDialog
from compas_viewer.components.datapanel import DataPanel
from compas_viewer.components.datapanel import _DataInventoryItem
from compas_viewer.components.datapanel import _DataReference
from compas_viewer.components.datapanel import _data_inventory
from compas_viewer.components.datastructureattributes import _ElementAttributesModel
from compas_viewer.config import Config
from compas_viewer.scene import ViewerScene
from compas_viewer.state import ViewerState


@pytest.fixture(scope="module", autouse=True)
def application():
    app = QApplication.instance() or QApplication([])
    yield app


def test_inventory_deduplicates_shared_items_and_appends_annotation_references():
    scene = ViewerScene()
    sphere = Sphere(1.0, name="Shared sphere")
    first = scene.add(sphere, name="First placement")
    second = scene.add(sphere, name="Second placement")
    annotation = scene.add_annotation(TextAnnotation("Note", [0, 0, 0]), name="Note entry")

    records = _data_inventory(scene)

    assert [record.guid for record in records] == [sphere.guid, annotation.item_guid]
    assert records[0].item is sphere
    assert [(ref.domain, ref.guid) for ref in records[0].references] == [("Scene", first.guid), ("Scene", second.guid)]
    assert records[1].references[0].domain == "Annotation"


def test_inventory_retains_unresolved_spatial_and_annotation_rows_without_resolution():
    scene = ViewerScene()
    spatial_guid = uuid4()
    annotation_guid = uuid4()
    scene.add_reference(spatial_guid, name="Missing shape")
    scene.add_annotation_entry(SceneAnnotation(item_guid=annotation_guid, name="Missing note"))

    records = _data_inventory(scene)

    assert [(record.guid, record.item, record.name, record.type_name) for record in records] == [
        (spatial_guid, None, "Missing shape", "Unknown"),
        (annotation_guid, None, "Missing note", "Unknown"),
    ]


def test_panel_selection_is_local_and_preserved_across_refresh(monkeypatch):
    scene = ViewerScene()
    first = scene.add(Sphere(1.0), name="First")
    second = scene.add(Sphere(2.0), name="Second")
    spatial_selection = SimpleNamespace(objects=(first,))
    annotation_selection = SimpleNamespace(entries=())
    viewer = SimpleNamespace(scene=scene, state=SimpleNamespace(selection=spatial_selection, annotation_selection=annotation_selection))
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))
    panel = DataPanel()
    panel.update()
    panel.table.selectRow(1)

    panel.update()

    assert panel.selected_guid == second.item_guid
    assert spatial_selection.objects == (first,)
    assert annotation_selection.entries == ()


def test_generic_details_never_reads_serialized_payload():
    class GuardedData(Data):
        def __init__(self, value: int) -> None:
            super().__init__()
            self.value = value

        @property
        def __data__(self):
            raise AssertionError("Data Details must not inspect __data__")

    item = GuardedData(42)
    record = _DataInventoryItem(item.guid, item, (_DataReference("Scene", uuid4(), "Guarded"),))

    dialog = DataDetailsDialog(record)

    table = dialog.findChild(QTableWidget)
    assert table is not None
    assert table.item(0, 0).text() == "value"
    assert table.item(0, 1).text() == "42"


def test_mesh_details_use_lazy_read_only_declared_domain_models(monkeypatch):
    mesh = Mesh.from_vertices_and_faces([[0, 0, 0], [1, 0, 0], [0, 1, 0]], [[0, 1, 2]])
    reads = []
    original = mesh.vertex_attribute

    def counted(key, name, *args):
        if not args:
            reads.append((key, name))
        return original(key, name, *args)

    monkeypatch.setattr(mesh, "vertex_attribute", counted)
    scene = ViewerScene()
    scene.add(mesh)

    dialog = DataDetailsDialog(_data_inventory(scene)[0])
    models = [table.model() for table in dialog.findChildren(QTableView) if isinstance(table.model(), _ElementAttributesModel)]

    assert models
    assert reads == []
    model = models[0]
    index = model.index(0, 1)
    assert not model.flags(index) & Qt.ItemFlag.ItemIsEditable
    assert not model.setData(index, 99)


def test_binding_refreshes_only_data_projection_without_renderer_work():
    scene = ViewerScene()
    sphere = Sphere(1.0)
    scene.add_reference(sphere.guid, name="Pending sphere")
    data_panel = SimpleNamespace(update=Mock())
    renderer = SimpleNamespace(rebuild_buffers=Mock(), update=Mock())
    viewer = SimpleNamespace(running=True, ui=SimpleNamespace(sidebar=SimpleNamespace(data_panel=data_panel)), renderer=renderer)
    scene.attach(viewer)

    scene.bind(sphere)

    data_panel.update.assert_called_once_with()
    renderer.rebuild_buffers.assert_not_called()
    renderer.update.assert_not_called()


def test_running_public_spatial_add_paths_refresh_immediately_and_preserve_selection(monkeypatch):
    scene = ViewerScene()
    renderer = SimpleNamespace(rebuild_buffers=Mock(), update=Mock())
    viewer = SimpleNamespace(scene=scene, running=True, renderer=renderer)
    monkeypatch.setattr(Base, "viewer", property(lambda _self: viewer))
    panel = DataPanel()
    viewer.ui = SimpleNamespace(sidebar=SimpleNamespace(data_panel=panel))
    scene.attach(viewer)
    first_guid = uuid4()

    scene.add_reference(first_guid, name="Pending")

    assert panel.table.rowCount() == 1
    assert panel.table.item(0, 2).text() == "Unresolved"
    panel.table.selectRow(0)
    sphere = Sphere(1.0)

    scene.add_object(SceneObject(item=sphere, name="Direct object"))

    assert panel.table.rowCount() == 2
    assert panel.selected_guid == first_guid
    assert panel.table.item(1, 2).text() == "Bound"
    renderer.rebuild_buffers.assert_not_called()
    renderer.update.assert_not_called()


def _attached_running_scene(scene):
    viewer = object.__new__(Viewer)
    viewer.running = True
    viewer._config = Config()
    viewer._scene = scene
    viewer._undo_transforms = []
    viewer._redo_transforms = []
    data_panel = Mock()
    sidebar = Mock()
    sidebar.data_panel = data_panel
    sidebar.update.side_effect = data_panel.update
    renderer = Mock()
    viewer.ui = SimpleNamespace(sidebar=sidebar, viewport=SimpleNamespace(renderer=renderer))
    scene.attach(viewer)
    viewer.state = ViewerState(
        viewer.config,
        lambda guid: scene.object(guid),
        lambda guid: scene.annotation(guid),
    )
    viewer.state.changed.connect(viewer._on_state_changed)
    return viewer, data_panel, sidebar, renderer


@pytest.mark.parametrize("domain", ["spatial", "annotation"])
@pytest.mark.parametrize("selected", [False, True])
def test_removal_refreshes_data_projection_once_with_or_without_selection_change(domain, selected):
    scene = ViewerScene()
    spatial = scene.add(Sphere(1.0), name="Sphere")
    annotation = scene.add_annotation(TextAnnotation("Note", [0, 0, 0]), name="Note")
    viewer, data_panel, sidebar, renderer = _attached_running_scene(scene)
    if selected:
        selection = viewer.state.selection if domain == "spatial" else viewer.state.annotation_selection
        selection.add(spatial if domain == "spatial" else annotation)
    data_panel.reset_mock()
    sidebar.reset_mock()
    sidebar.update.side_effect = data_panel.update
    renderer.reset_mock()

    if domain == "spatial":
        scene.remove(spatial)
    else:
        scene.remove_annotation(annotation)

    data_panel.update.assert_called_once_with()
    renderer.update.assert_called_once_with()
    if selected:
        sidebar.update.assert_not_called()
    else:
        sidebar.update.assert_called_once_with()


@pytest.mark.parametrize("selected", [False, True])
def test_clear_refreshes_data_projection_once_with_or_without_selection_changes(selected):
    scene = ViewerScene()
    spatial = scene.add(Sphere(1.0), name="Sphere")
    annotation = scene.add_annotation(TextAnnotation("Note", [0, 0, 0]), name="Note")
    viewer, data_panel, sidebar, renderer = _attached_running_scene(scene)
    if selected:
        viewer.state.selection.add(spatial)
        viewer.state.annotation_selection.add(annotation)
    data_panel.reset_mock()
    sidebar.reset_mock()
    sidebar.update.side_effect = data_panel.update
    renderer.reset_mock()

    scene.clear()

    data_panel.update.assert_called_once_with()
    assert renderer.update.call_count == (2 if selected else 1)
    renderer.rebuild_buffers.assert_called_once_with()
    if selected:
        sidebar.update.assert_not_called()
    else:
        sidebar.update.assert_called_once_with()


def test_generic_details_isolate_raising_properties_and_string_formatters():
    class BadString:
        def __str__(self) -> str:
            raise RuntimeError("cannot format")

    class HostileData(Data):
        def __init__(self, broken: object, printable: object) -> None:
            super().__init__()
            self.printable = printable

        @property
        def broken(self) -> object:
            raise RuntimeError("cannot read")

        @property
        def __data__(self):
            raise AssertionError("Data Details must not inspect __data__")

    item = HostileData(None, BadString())
    record = _DataInventoryItem(item.guid, item, (_DataReference("Scene", uuid4(), "Hostile"),))

    dialog = DataDetailsDialog(record)

    table = dialog.findChild(QTableWidget)
    assert table is not None
    assert table.rowCount() == 1
    assert table.item(0, 0).text() == "printable"
    assert table.item(0, 1).text() == "<unavailable: RuntimeError>"
