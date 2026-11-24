from pathlib import Path
from tempfile import TemporaryDirectory

from compas.colors import Color
from compas.data import json_dump
from compas.data import json_load
from compas.geometry import Box
from compas.geometry import Translation
from compas.scene import Scene
from compas.scene import TextAnnotation
from compas_viewer import Viewer

viewer = Viewer()
original = Box(1)
translated = Box(1)

original_object = viewer.scene.add(original, name="Original", surfacecolor=Color.blue())
viewer.scene.add(
    translated,
    name="Translated",
    surfacecolor=Color.red(),
    transformation=Translation.from_vector([2, 0, 0]),
)
note = TextAnnotation("Saved with the scene", [0.5, 0.5, 1.0])
note_entry = viewer.scene.add_annotation(note, name="Serialization note")
items = [original, translated, note]

# Selection belongs to the Viewer and is not part of the serialized Scene.
viewer.state.selection.add(original_object)

with TemporaryDirectory() as tempdir:
    scene_path = Path(tempdir) / "viewer-scene.json"
    data_path = Path(tempdir) / "viewer-data.json"
    json_dump(viewer.scene, scene_path)
    json_dump(items, data_path)
    loaded_scene = json_load(scene_path)
    loaded_items = json_load(data_path)

if not isinstance(loaded_scene, Scene):
    raise TypeError("The serialized file does not contain a COMPAS scene.")

object_names = [loaded_scene.object(node.object_guid).name for node in loaded_scene.nodes]
print(object_names)

loaded_note_entry = loaded_scene.annotations[0]
assert loaded_note_entry.guid == note_entry.guid
assert loaded_note_entry.item_guid == note.guid

loaded_scene.bind_many(loaded_items)
loaded_note = next(item for item in loaded_items if item.guid == note.guid)
assert loaded_note_entry.item is loaded_note

viewer.scene = loaded_scene
assert viewer.state.selection.objects == ()
viewer.show()
