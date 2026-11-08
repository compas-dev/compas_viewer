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


@pytest.mark.parametrize(
    ("relative_path", "expected_objects"),
    [
        ("docs/examples/object/points.py", 10),
        ("docs/examples/scene/groups.py", 4),
        ("docs/examples/configuration/window.py", 1),
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
