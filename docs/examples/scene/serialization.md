# Scene Serialization

Viewer scenes store a reference-only description of their spatial hierarchy,
ordered durable annotations, and display state. Hierarchy-only nodes contain
scene-object GUIDs; resolve each node through `Scene.object` to inspect its
stable semantic scene object. Annotation entries retain their own identity and
the GUID of their referenced annotation item. Save all referenced COMPAS data,
including annotation items, separately and bind it before assigning the scene
to a Viewer or drawing it.

The durable Viewer fields include resolution, display colors and sizes, mesh
display flags, transformations, visibility, and annotation presentation. The
example verifies that the text-annotation entry and its item reference retain
their GUIDs across the round trip. It then binds the independently loaded
annotation item. Interactive selection, Viewer Settings window state, picking
colors, GPU buffers, renderer caches, and other runtime state are deliberately
not serialized. Replacing the active scene therefore clears the setup-only
selection used by the example.

```python
--8<-- "docs/examples/scene/serialization.py"
```
