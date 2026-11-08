# Scene Serialization

Viewer scenes store a reference-only description of their hierarchy and durable
display state. Hierarchy-only nodes contain object GUIDs; resolve each node
through `Scene.object` to inspect its stable semantic scene object. Save the
referenced COMPAS data separately and bind it before assigning the scene to a
Viewer or drawing it.

The durable Viewer fields include resolution, display colors and sizes, mesh
display flags, transformations, and visibility. Interactive selection, picking
colors, GPU buffers, renderer caches, and other runtime state are deliberately
not serialized.

```python
--8<-- "docs/examples/scene/serialization.py"
```
