# Text Annotations

COMPAS scene annotations are backend-neutral and live in an ordered collection
outside the spatial hierarchy. Use `viewer.scene.add_annotation(...)` for text,
arrows, and dimensions; `viewer.scene.add(...)` is reserved for spatial scene
objects.

The Viewer renders text and arrows at their world-coordinate anchors and
resolves persistent distance dimensions when it draws the scene. A dimension
unit is an informational suffix; it does not convert coordinates.

`DimensionStyle` controls the dimension color, line width, text size, arrow
size, and label offset. Sizes and offsets use logical screen pixels. A positive
label offset moves the label toward the left side of the projected start-to-end
segment.

Omitting the style color uses magenta for a newly constructed default. An
explicit color remains authoritative, and a serialized style reloads its stored
color. Magenta is a visible starting point rather than a guarantee of contrast
against every viewport background.

```python
--8<-- "docs/examples/object/text_annotations.py"
```

The **Annotations** sidebar tab controls annotation names, visibility,
selection, removal, and the style of one selected distance dimension. The
ordered list and selected-annotation details occupy separate stable areas.
Annotations have no parent, children, or inherited transformation. Their
selection is independent from viewport and scene-tree object selection, and
switching tabs preserves both selections.
