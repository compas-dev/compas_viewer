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


def verify_scene(viewer):
    assert len(viewer.scene.objects) == expected_objects


Viewer.show = verify_scene
runpy.run_path(sys.argv[1], run_name="__main__")
"""
RUN_CALLBACK_EXAMPLE = """
import json
import runpy
import sys

from compas_viewer import Viewer

updates = []


class RenderObject:
    def update(self, *args, **kwargs):
        assert not args
        updates.append(kwargs)


Viewer.show = lambda self: None
namespace = runpy.run_path(sys.argv[1], run_name="__main__")
viewer = namespace["viewer"]
viewer.scene.render_object = lambda sceneobject: RenderObject()
namespace[sys.argv[2]](*json.loads(sys.argv[3]))
assert updates == json.loads(sys.argv[4])
"""


@pytest.mark.parametrize(
    ("relative_path", "expected_objects"),
    [
        ("docs/examples/object/points.py", 10),
        ("docs/examples/scene/groups.py", 4),
        ("docs/examples/configuration/window.py", 1),
        ("docs/examples/dynamic/orbiting.py", 1),
        ("docs/examples/ui/camera.py", 25),
        ("docs/examples/ui/object_inspection.py", 2),
        ("docs/examples/ui/sidedock.py", 1),
    ],
)
def test_documentation_example_smoke(relative_path, expected_objects):
    environment = os.environ.copy()
    environment["QT_QPA_PLATFORM"] = "offscreen"
    subprocess.run(
        [sys.executable, "-c", RUN_EXAMPLE, str(ROOT / relative_path), str(expected_objects)],
        check=True,
        cwd=ROOT,
        env=environment,
    )


@pytest.mark.parametrize(
    ("relative_path", "callback", "callback_args", "expected_updates"),
    [
        ("docs/examples/dynamic/dynamic.py", "move_point", [1], [{"update_data": True}]),
        ("docs/examples/dynamic/dynamic_mesh.py", "deform_mesh", [1], [{"update_data": True}]),
        (
            "docs/examples/dynamic/shared_geometry.py",
            "deform_mesh",
            [1],
            [
                {"update_transform": True, "update_data": True},
                {"update_transform": False, "update_data": True},
                {"update_transform": True, "update_data": False},
            ],
        ),
        ("docs/examples/dynamic/transform.py", "transform_objects", [1], [{}, {}, {}]),
        ("docs/examples/ui/sidedock.py", "move_box", [None, 1.0], [{}]),
    ],
)
def test_documentation_callback_refreshes_render_object(relative_path, callback, callback_args, expected_updates):
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
            json.dumps(expected_updates),
        ],
        check=True,
        cwd=ROOT,
        env=environment,
    )
