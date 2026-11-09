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


@pytest.mark.parametrize(
    ("relative_path", "expected_objects", "expected_annotations"),
    [
        ("docs/examples/object/points.py", 10, 0),
        ("docs/examples/scene/groups.py", 3, 1),
        ("docs/examples/configuration/window.py", 1, 0),
        ("docs/examples/dynamic/orbiting.py", 1, 0),
        ("docs/examples/dynamic/transform.py", 2, 0),
        ("docs/examples/ui/camera.py", 25, 0),
        ("docs/examples/ui/object_inspection.py", 2, 0),
        ("docs/examples/ui/sidedock.py", 1, 0),
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
