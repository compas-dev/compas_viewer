# Shared Geometry Updates

Multiple stable scene objects can reference the same mesh. A geometry refresh
regenerates render data and buffers after the shared mesh changes. A transform
refresh synchronizes direct external transformation assignments without
regenerating geometry.

```python
--8<-- "docs/examples/dynamic/shared_geometry.py"
```
