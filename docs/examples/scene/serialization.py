from pathlib import Path
from tempfile import TemporaryDirectory

from compas.colors import Color
from compas.data import json_dump
from compas.data import json_load
from compas.geometry import Box
from compas.geometry import Translation
from compas.scene import Scene
from compas_viewer import Viewer

viewer = Viewer()
viewer.scene.add(Box(1), name="Original", facecolor=Color.blue())
viewer.scene.add(
    Box(1),
    name="Translated",
    facecolor=Color.red(),
    transformation=Translation.from_vector([2, 0, 0]),
)

with TemporaryDirectory() as tempdir:
    filepath = Path(tempdir) / "viewer-scene.json"
    json_dump(viewer.scene, filepath)
    loaded_scene = json_load(filepath)

if not isinstance(loaded_scene, Scene):
    raise TypeError("The serialized file does not contain a COMPAS scene.")

viewer.scene = loaded_scene
viewer.show()
