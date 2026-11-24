import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
RUN_EXAMPLE = """
import runpy
import sys

from compas_viewer import Viewer

expected_objects = int(sys.argv[2])
expected_annotations = int(sys.argv[3])


def verify_scene(viewer):
    assert len(viewer.scene.objects) == expected_objects
    assert len(viewer.scene.annotations) == expected_annotations


Viewer.show = verify_scene
runpy.run_path(sys.argv[1], run_name="__main__")
"""
RUN_CALLBACK_EXAMPLE = """
import json
import runpy
import sys

from compas_viewer import Viewer

refreshes = []


def record_refresh(name):
    def refresh(self, objects=None):
        count = None if objects is None else len(tuple(objects))
        refreshes.append([name, count])

    return refresh

Viewer.refresh_geometry = record_refresh("geometry")
Viewer.refresh_appearance = record_refresh("appearance")
Viewer.refresh_transform = record_refresh("transform")
Viewer.show = lambda self: None
namespace = runpy.run_path(sys.argv[1], run_name="__main__")
namespace[sys.argv[2]](*json.loads(sys.argv[3]))
assert refreshes == json.loads(sys.argv[4])
"""
RUN_VIEWER_SETTINGS_EXAMPLE = """
import runpy
import sys

from PySide6.QtWidgets import QApplication

from compas_viewer import Viewer

Viewer.show = lambda self: None
namespace = runpy.run_path(sys.argv[1], run_name="__main__")
viewer = namespace["viewer"]
settings = viewer.ui.settings
widget = settings.widget

assert viewer.settings_items == namespace["settings_items"]
assert viewer.settings_items is not namespace["settings_items"]
assert list(settings.sections) == ["Camera", "Display", "Grid and Units"]
assert not widget.isVisible()

focused_sections = []
focus_section = settings.focus_section
settings.focus_section = lambda name: (focused_sections.append(name), focus_section(name))[1]
namespace["open_camera_settings"]()
QApplication.processEvents()
assert settings.widget is widget
assert widget.isVisible()
assert focused_sections
assert set(focused_sections) == {"Camera"}

settings.show("Display")
QApplication.processEvents()
assert settings.widget is widget
assert widget.isVisible()

widget.close()
QApplication.processEvents()
assert not widget.isVisible()
"""
RUN_OBJECT_INSPECTION_EXAMPLE = """
import runpy
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QTableView
from PySide6.QtWidgets import QTableWidget
from PySide6.QtWidgets import QTabWidget

from compas.datastructures import Graph
from compas.datastructures import Mesh
from compas_viewer import Viewer
from compas_viewer.components.datapanel import DataDetailsDialog


def verify_inspector(viewer: Viewer) -> None:
    '''Verify the advertised read-only and opt-in inspection surfaces.'''
    assert hasattr(viewer.ui.sidebar, "datastructure_attributes")
    assert any(item.get("type") == "DatastructureAttributes" for item in viewer.sidebar_items)

    sceneobjects = viewer.scene.objects
    mesh_object = next(obj for obj in sceneobjects if isinstance(obj.item, Mesh))
    graph_object = next(obj for obj in sceneobjects if isinstance(obj.item, Graph))
    mesh = mesh_object.item
    graph = graph_object.item

    panel = viewer.ui.sidebar.data_panel
    panel.update()
    mesh_record = panel._records[mesh.guid]
    graph_record = panel._records[graph.guid]
    assert len(mesh_record.references) == 2

    mesh_details = DataDetailsDialog(mesh_record)
    mesh_tabs = mesh_details.findChild(QTabWidget)
    assert [mesh_tabs.tabText(index) for index in range(mesh_tabs.count())] == [
        "Parameters",
        "General Attributes",
        "Vertices",
        "Edges",
        "Faces",
    ]
    general = mesh_tabs.widget(1)
    assert isinstance(general, QTableWidget)
    assert general.editTriggers() == QAbstractItemView.EditTrigger.NoEditTriggers
    assert [general.item(row, 0).text() for row in range(general.rowCount())] == [
        "discipline",
        "revision",
    ]

    vertices = mesh_tabs.widget(2)
    assert isinstance(vertices, QTableView)
    model = vertices.model()
    temperature_column = next(
        column
        for column in range(model.columnCount())
        if model.headerData(column, Qt.Orientation.Horizontal) == "temperature"
    )
    assert model.data(model.index(0, temperature_column)) == "20.0"
    assert model.data(model.index(2, temperature_column)) == "45.0"
    assert not model.flags(model.index(2, temperature_column)) & Qt.ItemFlag.ItemIsEditable

    graph_details = DataDetailsDialog(graph_record)
    graph_tabs = graph_details.findChild(QTabWidget)
    assert [graph_tabs.tabText(index) for index in range(graph_tabs.count())] == [
        "Parameters",
        "General Attributes",
        "Nodes",
        "Edges",
    ]

    details_text = viewer.ui.sidebar.object_setting._details_text([mesh_object])
    section_names = [
        "Identity",
        "General Scene State",
        "Type-Specific Scene State",
        "Represented Item Parameters",
    ]
    section_positions = [details_text.index(name) for name in section_names]
    assert section_positions == sorted(section_positions)
    assert "compas.scene.MeshObject.show_faces:" in details_text


Viewer.show = verify_inspector
runpy.run_path(sys.argv[1], run_name="__main__")
"""


@pytest.mark.parametrize(
    ("relative_path", "expected_objects", "expected_annotations"),
    [
        ("docs/examples/object/points.py", 10, 0),
        ("docs/examples/scene/groups.py", 3, 1),
        ("docs/examples/configuration/window.py", 1, 0),
        ("docs/examples/dynamic/orbiting.py", 1, 0),
        ("docs/examples/dynamic/transform.py", 2, 0),
        ("docs/examples/scene/serialization.py", 2, 1),
        ("docs/examples/ui/camera.py", 25, 0),
        ("docs/examples/ui/measurements.py", 1, 0),
        ("docs/examples/ui/object_inspection.py", 4, 0),
        ("docs/examples/ui/overlays.py", 1, 0),
        ("docs/examples/ui/sidedock.py", 1, 0),
        ("docs/examples/ui/viewer_settings.py", 2, 2),
    ],
)
def test_documentation_example_smoke(relative_path, expected_objects, expected_annotations):
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    subprocess.run(
        [sys.executable, "-c", RUN_EXAMPLE, str(ROOT / relative_path), str(expected_objects), str(expected_annotations)],
        check=True,
        cwd=ROOT,
        env=environment,
    )


@pytest.mark.parametrize(
    ("relative_path", "callback", "callback_args", "expected_refreshes"),
    [
        ("docs/examples/dynamic/dynamic.py", "move_point", [1], [["geometry", 1]]),
        ("docs/examples/dynamic/dynamic_mesh.py", "deform_mesh", [1], [["geometry", 1]]),
        (
            "docs/examples/dynamic/shared_geometry.py",
            "deform_mesh",
            [1],
            [["geometry", None], ["transform", 2]],
        ),
        ("docs/examples/ui/sidedock.py", "toggle_box", [], [["appearance", 1]]),
        ("docs/examples/ui/sidedock.py", "move_box", [None, 1.0], [["transform", 1]]),
        ("docs/examples/ui/sidedock.py", "refresh_viewer", [None, 1.0], [["appearance", 1]]),
    ],
)
def test_documentation_callback_uses_public_refresh(relative_path, callback, callback_args, expected_refreshes):
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    subprocess.run(
        [
            sys.executable,
            "-c",
            RUN_CALLBACK_EXAMPLE,
            str(ROOT / relative_path),
            callback,
            json.dumps(callback_args),
            json.dumps(expected_refreshes),
        ],
        check=True,
        cwd=ROOT,
        env=environment,
    )


@pytest.mark.parametrize(
    ("relative_path", "runner"),
    [
        ("docs/examples/ui/viewer_settings.py", RUN_VIEWER_SETTINGS_EXAMPLE),
        ("docs/examples/ui/object_inspection.py", RUN_OBJECT_INSPECTION_EXAMPLE),
    ],
)
def test_documentation_ui_composition_is_effective(relative_path, runner):
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    subprocess.run(
        [sys.executable, "-c", runner, str(ROOT / relative_path)],
        check=True,
        cwd=ROOT,
        env=environment,
    )
