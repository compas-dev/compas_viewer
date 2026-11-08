# Text Annotations

COMPAS scene annotations are backend-neutral. The Viewer renders text and arrows
in world space and resolves persistent distance dimensions when it draws the
scene. A dimension unit is an informational suffix; it does not convert the
coordinates.

```python
--8<-- "docs/examples/object/text_annotations.py"
```
