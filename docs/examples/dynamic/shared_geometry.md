# Shared Geometry Updates

Multiple stable scene objects can reference the same mesh while their transient
Viewer render objects refresh geometry and transformations independently. A
data refresh reads the shared mesh again; a transform refresh affects only the
corresponding scene object.

```python
--8<-- "docs/examples/dynamic/shared_geometry.py"
```
