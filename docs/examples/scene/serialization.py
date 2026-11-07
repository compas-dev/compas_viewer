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
original = Box(1)
translated = Box(1)
items = [original, translated]

viewer.scene.add(original, name="Original", facecolor=Color.blue())
viewer.scene.add(
    translated,
    name="Translated",
    facecolor=Color.red(),
    transformation=Translation.from_vector([2, 0, 0]),
)

with TemporaryDirectory() as tempdir:
    scene_path = Path(tempdir) / "viewer-scene.json"
    data_path = Path(tempdir) / "viewer-data.json"
    json_dump(viewer.scene, scene_path)
    json_dump(items, data_path)
    loaded_scene = json_load(scene_path)
    loaded_items = json_load(data_path)

if not isinstance(loaded_scene, Scene):
    raise TypeError("The serialized file does not contain a COMPAS scene.")

node_names = [node.name for node in loaded_scene.nodes]
print(node_names)

loaded_scene.bind_many(loaded_items)
loaded_scene.bind_context("Viewer")
viewer.scene = loaded_scene
viewer.show()
