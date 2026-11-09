# Dynamic Point

The scene object stores durable display state, while the Viewer owns transient
render buffers. After changing the represented point, call
`viewer.refresh_geometry(...)` to regenerate its render data.

![](../../assets/images/dynamic.gif)

```python
--8<-- "docs/examples/dynamic/dynamic.py"
```
