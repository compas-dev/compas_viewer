from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from compas.data import json_dumps
from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas.scene import SceneItemNotBoundError
from compas_viewer import Viewer
from compas_viewer.commands import zoom_extents
from compas_viewer.components.datastructureattributes import DatastructureAttributes
from compas_viewer.components.datastructureattributes import _element_domains
from compas_viewer.components.datastructureattributes import _ElementAttributesModel
from compas_viewer.config import Config
from compas_viewer.scene import ViewerScene
from compas_viewer.state import ViewerState
from compas_viewer.uidefinitions import default_sidebar_items


@pytest.fixture(scope="module", autouse=True)
def application():
    app = QApplication.instance() or QApplication([])
    yield app


def make_mesh() -> Mesh:
    mesh = Mesh.from_vertices_and_faces(
        [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        [[0, 1, 2]],
    )
    mesh.update_default_vertex_attributes(
        {
            "active": False,
            "count": 1,
            "weight": 1.5,
            "label": "default",
            "unsupported": [],
            "unknown": None,
        }
    )
    mesh.update_default_edge_attributes({"crease": 0.0})
    mesh.update_default_face_attributes({"region": "A"})
    return mesh


def model_for(domain, changed=None, failed=None):
    return _ElementAttributesModel(
        domain,
        changed=changed or (lambda: None),
        failed=failed or (lambda error: None),
    )


def test_mesh_domains_use_declared_default_order_and_omit_sparse_attributes():
    mesh = make_mesh()
    mesh.vertex_attribute(0, "sparse", "local")

    domains = _element_domains(mesh)

    assert [domain.name for domain in domains] == ["vertices", "edges", "faces"]
    vertices = model_for(domains[0])
    assert vertices.attributes == tuple(mesh.default_vertex_attributes)
    assert "sparse" not in vertices.attributes
    assert vertices.rowCount() == 3
    assert vertices.headerData(0, Qt.Orientation.Horizontal) == "Key"
    assert vertices.headerData(vertices.attributes.index("label") + 1, Qt.Orientation.Horizontal) == "label"


def test_graph_domains_use_nodes_and_declared_edges_only():
    graph = Graph()
    graph.add_node(0, x=0.0, y=0.0, z=0.0)
    graph.add_node(1, x=1.0, y=0.0, z=0.0)
    graph.add_edge(0, 1)

    assert [domain.name for domain in _element_domains(graph)] == ["nodes"]

    graph.update_default_edge_attributes({"category": "primary"})

    assert [domain.name for domain in _element_domains(graph)] == ["nodes", "edges"]


def test_declared_domain_may_have_zero_rows():
    mesh = Mesh()

    vertices = model_for(_element_domains(mesh)[0])

    assert vertices.columnCount() == 4
    assert vertices.rowCount() == 0


def test_large_model_snapshots_keys_without_reading_attribute_values(monkeypatch):
    mesh = Mesh()
    for index in range(1000):
        mesh.add_vertex(index, x=float(index), y=0.0, z=0.0)
    reads = []
    original = mesh.vertex_attribute

    def counted(key, name, *args):
        if not args:
            reads.append((key, name))
        return original(key, name, *args)

    monkeypatch.setattr(mesh, "vertex_attribute", counted)

    model = model_for(_element_domains(mesh)[0])

    assert model.rowCount() == 1000
    assert reads == []

    index = model.index(999, model.attributes.index("x") + 1)
    assert model.data(index, Qt.ItemDataRole.DisplayRole) == "999.0"
    assert reads == [(999, "x")]


def test_model_edits_supported_scalar_types_through_singular_setter():
    mesh = make_mesh()
    model = model_for(_element_domains(mesh)[0])

    values = {
        "active": True,
        "count": 3,
        "weight": 2,
        "label": "changed",
    }
    for name, value in values.items():
        index = model.index(0, model.attributes.index(name) + 1)
        assert model.setData(index, value)

    assert mesh.vertex_attribute(0, "active") is True
    assert mesh.vertex_attribute(0, "count") == 3
    assert type(mesh.vertex_attribute(0, "count")) is int
    assert mesh.vertex_attribute(0, "weight") == 2.0
    assert type(mesh.vertex_attribute(0, "weight")) is float
    assert mesh.vertex_attribute(0, "label") == "changed"


def test_boolean_cells_support_check_state_editing():
    mesh = make_mesh()
    model = model_for(_element_domains(mesh)[0])
    index = model.index(0, model.attributes.index("active") + 1)

    assert model.data(index, Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Unchecked
    assert model.setData(index, Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    assert mesh.vertex_attribute(0, "active") is True


def test_unsupported_and_none_defaults_remain_read_only():
    model = model_for(_element_domains(make_mesh())[0])

    for name in ("unsupported", "unknown"):
        index = model.index(0, model.attributes.index(name) + 1)
        assert not model.flags(index) & Qt.ItemFlag.ItemIsEditable
        assert not model.setData(index, "replacement")


def test_invalid_conversion_reports_original_error_without_refresh():
    errors = []
    refreshed = []
    model = model_for(
        _element_domains(make_mesh())[0],
        changed=lambda: refreshed.append(True),
        failed=errors.append,
    )
    index = model.index(0, model.attributes.index("count") + 1)

    assert not model.setData(index, 2.5)
    assert isinstance(errors[0], TypeError)
    assert refreshed == []


def test_mutation_failure_rereads_cell_and_does_not_refresh(monkeypatch):
    mesh = make_mesh()
    domain = _element_domains(mesh)[0]
    errors = []
    refreshed = []
    original = mesh.vertex_attribute

    def reject(key, name, *args):
        if args:
            raise ValueError("rejected")
        return original(key, name)

    monkeypatch.setattr(mesh, "vertex_attribute", reject)
    model = model_for(domain, changed=lambda: refreshed.append(True), failed=errors.append)
    index = model.index(0, model.attributes.index("label") + 1)

    assert not model.setData(index, "changed")
    assert str(errors[0]) == "rejected"
    assert refreshed == []
    assert model.data(index, Qt.ItemDataRole.EditRole) == "default"


def test_reset_removes_override_and_restores_effective_default():
    mesh = make_mesh()
    mesh.vertex_attribute(0, "label", "override")
    refreshed = []
    model = model_for(_element_domains(mesh)[0], changed=lambda: refreshed.append(True))
    index = model.index(0, model.attributes.index("label") + 1)

    assert model.reset_to_default(index)
    assert mesh.vertex_attribute(0, "label") == "default"
    assert refreshed == [True]


def test_edge_keys_remain_exact_and_are_only_formatted_for_display():
    mesh = make_mesh()
    edges = model_for(_element_domains(mesh)[1])
    key = edges.keys[0]

    assert isinstance(key, tuple)
    assert edges.data(edges.index(0, 0), Qt.ItemDataRole.DisplayRole) == repr(key)


def test_edge_key_passes_unchanged_to_singular_setter_and_unsetter(monkeypatch):
    mesh = make_mesh()
    original_attribute = mesh.edge_attribute
    original_unset = mesh.unset_edge_attribute
    set_keys = []
    unset_keys = []

    def capture_set(key, name, *args):
        if args:
            set_keys.append(key)
        return original_attribute(key, name, *args)

    def capture_unset(key, name):
        unset_keys.append(key)
        return original_unset(key, name)

    monkeypatch.setattr(mesh, "edge_attribute", capture_set)
    monkeypatch.setattr(mesh, "unset_edge_attribute", capture_unset)
    model = model_for(_element_domains(mesh)[1])
    key = model.keys[0]
    index = model.index(0, model.attributes.index("crease") + 1)

    assert model.setData(index, 0.5)
    assert model.reset_to_default(index)
    assert set_keys == [key]
    assert unset_keys == [key]
    assert set_keys[0] is key
    assert unset_keys[0] is key


def test_component_builds_tabs_without_mutating_datastructure(monkeypatch):
    mesh = make_mesh()
    sceneobject = SimpleNamespace(item=mesh)
    scene = SimpleNamespace(objects=[sceneobject])
    selection = SimpleNamespace(objects=(sceneobject,))
    viewer = SimpleNamespace(scene=scene, state=SimpleNamespace(selection=selection))
    monkeypatch.setattr(DatastructureAttributes, "viewer", property(lambda self: viewer), raising=False)
    before = json_dumps(mesh)

    component = DatastructureAttributes()
    component.update()

    assert [component.tabs.tabText(index) for index in range(component.tabs.count())] == ["Vertices", "Edges", "Faces"]
    assert json_dumps(mesh) == before


def test_component_refreshes_render_data_and_relevant_ui_after_edit(monkeypatch):
    mesh = make_mesh()
    sceneobject = SimpleNamespace(item=mesh)
    calls = []
    render_object = SimpleNamespace(
        refresh_data=lambda: calls.append(("refresh", {})),
        update=lambda **kwargs: calls.append(("render", kwargs)),
    )
    scene = SimpleNamespace(
        objects=[sceneobject],
        render_object=lambda obj: render_object,
    )
    sidebar = SimpleNamespace(
        sceneform=SimpleNamespace(update=lambda **kwargs: calls.append(("scene", kwargs))),
        object_setting=SimpleNamespace(update=lambda: calls.append(("object", {}))),
    )
    viewer = SimpleNamespace(
        scene=scene,
        state=SimpleNamespace(selection=SimpleNamespace(objects=(sceneobject,))),
        renderer=SimpleNamespace(update=lambda: calls.append(("renderer", {}))),
        ui=SimpleNamespace(sidebar=sidebar),
    )
    monkeypatch.setattr(DatastructureAttributes, "viewer", property(lambda self: viewer), raising=False)
    component = DatastructureAttributes()
    component.update()
    table = component.tabs.widget(0)
    assert table is not None
    model = table.model()
    assert isinstance(model, _ElementAttributesModel)
    index = model.index(0, model.attributes.index("label") + 1)

    assert model.setData(index, "changed")

    assert mesh.vertex_attribute(0, "label") == "changed"
    assert calls == [
        ("refresh", {}),
        ("render", {"update_data": True}),
        ("renderer", {}),
        ("scene", {"refresh": True}),
        ("object", {}),
    ]


@pytest.mark.parametrize("kind", ["mesh", "graph"])
def test_coordinate_edit_refreshes_bounds_consumed_by_zoom(monkeypatch, kind):
    if kind == "mesh":
        item = Mesh.from_vertices_and_faces(
            [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            [[0, 1, 2]],
        )
    else:
        item = Graph()
        item.add_node(0, x=0.0, y=0.0, z=0.0)
        item.add_node(1, x=1.0, y=0.0, z=0.0)
        item.add_edge(0, 1)

    runtime = Viewer()
    scene = ViewerScene()
    sidebar = SimpleNamespace(
        sceneform=SimpleNamespace(update=lambda **kwargs: None),
        object_setting=SimpleNamespace(update=lambda: None),
    )
    viewer = SimpleNamespace(
        scene=scene,
        state=ViewerState(Config(), scene.object),
        renderer=runtime.renderer,
        ui=SimpleNamespace(sidebar=sidebar),
        running=False,
    )
    scene.attach(viewer)
    sceneobject = scene.add(item)
    viewer.state.selection.add(sceneobject)
    render_object = scene.render_object(sceneobject)
    render_object.refresh_data()
    buffer_updates = []
    monkeypatch.setattr(render_object, "update", lambda **kwargs: buffer_updates.append(kwargs))
    monkeypatch.setattr(DatastructureAttributes, "viewer", property(lambda self: viewer), raising=False)
    component = DatastructureAttributes()
    component.update()
    table = component.tabs.widget(0)
    assert table is not None
    model = table.model()
    assert isinstance(model, _ElementAttributesModel)
    row = model.keys.index(1)
    index = model.index(row, model.attributes.index("x") + 1)

    assert float(render_object.bounding_box[1][0]) == 1.0
    assert model.setData(index, 10.0)
    assert float(render_object.bounding_box[1][0]) == 10.0
    assert buffer_updates == [{"update_data": True}]

    zoom_extents(viewer)

    assert viewer.renderer.camera.target.x == 5.0


def test_empty_reset_selection_performs_no_mutation_or_refresh(monkeypatch):
    mesh = make_mesh()
    sceneobject = SimpleNamespace(item=mesh)

    def fail_render(obj):
        raise AssertionError("empty reset must not refresh render state")

    scene = SimpleNamespace(
        objects=[sceneobject],
        render_object=fail_render,
    )
    selection = SimpleNamespace(objects=(sceneobject,))
    viewer = SimpleNamespace(scene=scene, state=SimpleNamespace(selection=selection))
    unset_calls = []
    monkeypatch.setattr(mesh, "unset_vertex_attribute", lambda key, name: unset_calls.append((key, name)))
    monkeypatch.setattr(DatastructureAttributes, "viewer", property(lambda self: viewer), raising=False)
    component = DatastructureAttributes()
    component.update()

    component.reset_selected()

    assert unset_calls == []


def test_switching_selected_object_rebuilds_domain_tabs(monkeypatch):
    mesh = make_mesh()
    graph = Graph()
    graph.add_node(10, x=0.0, y=0.0, z=0.0)
    mesh_object = SimpleNamespace(item=mesh)
    graph_object = SimpleNamespace(item=graph)
    selected = [mesh_object]
    scene = SimpleNamespace(objects=[mesh_object, graph_object])

    class Selection:
        @property
        def objects(self):
            return tuple(selected)

    viewer = SimpleNamespace(scene=scene, state=SimpleNamespace(selection=Selection()))
    monkeypatch.setattr(DatastructureAttributes, "viewer", property(lambda self: viewer), raising=False)
    component = DatastructureAttributes()

    component.update()
    assert [component.tabs.tabText(index) for index in range(component.tabs.count())] == ["Vertices", "Edges", "Faces"]

    selected[:] = [graph_object]
    component.update()

    assert [component.tabs.tabText(index) for index in range(component.tabs.count())] == ["Nodes"]
    model = component.tabs.widget(0).model()
    assert isinstance(model, _ElementAttributesModel)
    assert model.domain.item is graph
    assert model.keys == (10,)


def test_unresolved_selected_item_shows_message_without_loading_or_rendering(monkeypatch):
    class UnresolvedObject:
        reads = 0

        @property
        def item(self):
            self.reads += 1
            raise SceneItemNotBoundError("object", "item")

    sceneobject = UnresolvedObject()

    def fail_render(obj):
        raise AssertionError("unresolved data must not create render state")

    scene = SimpleNamespace(
        objects=[sceneobject],
        render_object=fail_render,
    )
    selection = SimpleNamespace(objects=(sceneobject,))
    viewer = SimpleNamespace(scene=scene, state=SimpleNamespace(selection=selection))
    monkeypatch.setattr(DatastructureAttributes, "viewer", property(lambda self: viewer), raising=False)
    component = DatastructureAttributes()

    component.update()

    assert sceneobject.reads == 1
    assert component.tabs.count() == 0
    assert component.message.text() == "The selected data is not bound"


def test_default_sidebar_does_not_include_datastructure_attributes():
    types = [item["type"] for item in default_sidebar_items()]

    assert "DatastructureAttributes" not in types
