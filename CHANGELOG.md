# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
* Added terminal activation of the viewer.
* Added `installation` documentation.
* Added documentations: index, api, etc. Mockups style is improved.
* Added `DeleteSelected` action class.
* Added `DataType` as the data type template for generating the buffer.
* Added `NetworkObject` for the scene objects.
* Added `compas_viewer.scene.ViewerSceneObject.LINEWIDTH_SELECTION_INCREMENTAL` to enhance line width for selection only.
* Added `BRepObject`, `CapsuleObject`, `ConeObject`, `CylinderObject`, `PlaneObject`, `SphereObject`, `EllipseObject`, `TorusObject`, `PolygonObject`, `PolylineObject`, `BoxObject`. The geometric resolution is handled by the `compas_viewer.scene.ViewerSceneObject.LINEARDEFLECTION`.
* Added `VectorObject` for the scene objects with mesh-based display for better visual effect.
* Added "instance" render mode for debugging and geometric analysis.
* Added contents in the `README.md`.
* Added full support for selection: drag_selection, drag_deselection, multiselect, deselect, select.
* Added `SelectAll` action class.
* Added `LookAt` action class.
* Added `compas_viewer.Viewer.add_action` for adding actions to the viewer.
* Added `Signal` structure for the `Action` class.
* Added complete key, mouse and modifier support from `PySide6`.
* Added `ZoomSelected` and `GLInfo` classes as template action classes.
* Added `Action` class.
* Added `Controller` class for the controller.
* Added `Grid` and `GridObject` for the scene objects.
* Added `TagObject`, `LineObject` and `PointObject` for the scene objects.
* Added test files for configurations.
* Added doc build, and many doc-building syntax fixes.
* Added `scene.json` for storing the scene configurations. Mostly store the default appearance features of the objects.
* `compas` recognizes `compas_viewer` context, and map the according `compas_viewer` objects to the `compas` objects.
* Added two main scene objects: `ViewerSceneObject` and `MeshObject`. `BufferObject` no longer exists but replaced by `ViewerSceneObject`.
* Added `add` function in the `Viewer` class for adding objects to the scene, which is also the entry for imputing user-defined attributes.
* Added and formatted `Shader` and `Camera`.
* Added a `RenderConfig` for configuring the Render object.
* Added the `shaders` and the `Shader` class in the shader folder.
* Created the `Camera`, `metrics` and `gl` functions and classes (most copied from the view2).
* Adjustment of the `ControllerConfig` and `ViewerConfig``.
* Adjustment of the `Viewer`.
* Basic `Viewer` buildup with the widgets.
* Configurations: `controller_config` and `viewer_config`
* Code and File structure diagrams.
* Added `NetworkObject`.

### Changed
* The `Index` page.
* Typing hints improved, now `compas_viewer` only support Python 3.9+.
* Introduce decorator @lru_cache() to reduce duplicate calculations. 
* Refactored the `Selector` and the instance_map structure, the main frame rate is higher and selection action is faster.
* Fixed the bug of the `Selector`, drag selection is now more accurate.
* More performative instance map and QObject-based selection architecture.
* Naming of the keys, mouses, and modifiers are changed. The key string which is the same as what it was called in the PySide6.QtCore.Qt, with lowercases and with prefix&underscores removed.
* `Grid` object inherits from `compas.data.Data`.
* Update the compatibility of the `ViewerSceneObject` to the core `SceneObject`.
* Refactored the `ControllerConfig`.
* Fix Qt package of `PySide6`.
* Moved `gl` from `render` folder to the `utilities` folder.
* All color representations are now in `compas.colors.Color`.
* Reduce the `numpy.array` representation. Mostly use `list` instead for clarity.
* Comments improved and better type hints.

### Removed
* Removed `self.objects` from the `Render` class.`
* Replace the `Grid` and `GridObject` but by `FrameObject`, which also hooks the `Frame` in compas.
