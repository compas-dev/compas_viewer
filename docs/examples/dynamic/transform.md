# Transform Scene Objects

Apply one world-space transformation to multiple scene objects, then undo and
redo the complete transaction. The Viewer validates every target before it
changes any object.

```python
--8<-- "docs/examples/dynamic/transform.py"
```

`transform_objects` currently accepts only `space="world"`. A request that
contains both an ancestor and its descendant is rejected because applying the
same world-space delta to both would be ambiguous.
