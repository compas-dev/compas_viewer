# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added `compas_viewer.components.dialog` component which handle camera setting popup window.

### Changed

* Fixed `action` bug.

### Removed


## [1.1.5] 2024-05-15

### Added

* Added `@viewer.on`.

### Changed

### Removed


## [1.1.4] 2024-05-14

### Added

* Added `button`, `double_edit` and `treeform` components.

### Changed

### Removed


## [1.1.3] 2024-05-14

### Added

* Added `PointcloudObject`.
* Added `compas_viewer.base.Base` to access viewer singleton.
* Added `compas_viewer.singleton.SingletonMeta` and `compas_viewer.singleton.Singleton`.
* Added `compas_viewer.scene.Group` and `compas_viewer.scene.GroupObject`.
* Added `PolyhedronObject`.
* Added `compas_viewer.scene.NurbsCurveObject`.

### Changed

* Changed `NurbsSurfaceObject` to use tessellation function of `OCCBrep`, show boundary curves instead of control curves.
* Renamed all lazy setup functions to `lazy_init`.
* Fixed camera initialization issue.
* Fixed and brought back `CollectionObject`.
* Updated objects color settings to align to `pointcolor`, `linecolor`, `facecolor`.
* Updated objects visibility settings to align to `show_points`, `show_lines`, `show_faces`.
* Updated objects drawing settings to align to `linewidth`, `pointsize`.
* Updated `PolygonObject` show faces.

### Removed

* removed `PyOpenGL-accelerate` from requirements.txt

## [1.1.2] 2024-04-22

### Added
* Added singletone `compas_viewer.viewer`
* Added singletone `compas_viewer.config`
* Added `compas_viewer.ui.ui` and `compas_viewer.components`.
### Changed
* Changed `compas_viewer.layout` to `compas_viewer.ui.ui`.
### Removed
* Removed old version of `compas_viewer.viewer`.

## [1.1.1] 2024-04-22

### Added

* Added non-python files to the release.

### Changed

### Removed


## [1.1.0] 2024-04-22

### Added

* Added `*args` in the `Viewer.add` method, resolve [#85](https://github.com/compas-dev/compas_viewer/issues/85).
* Added `Transformation` and `Visualization` sections for the `Propertyform`.
* Added `Propertyform` and its example in the documentation.
* Added example `layout/tree_view`.
* Added functionality of multiple widgets in main viewport.
* Added example `object/scale.py`.
* Added `RobotModelObject` and its example in the documentation.
* Added support to pinch gesture for zooming on touch pads.

### Changed
* Pin the `PySide6` version to `6.6.1`.
* Auto set the camera scale when `zoom_extend` is called.
* Updated the `Tag` example.
* Updated the `RobotModelObject` example.
* Update examples in the documentation.
* Renamed `surfaces` into `viewmesh` in every `ViewerGeometryObject`.
* Renamed `scene.json` to `viewer.json` and `scene_config` to `viewer_config`.
* Unify color naming. variables that control the colors of geometries are `surfacecolor`, `linecolor`,`pointcolor`, yet variables that control the colors of meshes are `facecolor`, `edgecolor`, `vertexcolor`.
* Added `ViewerGeometryObject` as the abstract class for all the geometry objects. Other specific geometry objects are inherited from this class.
* Changed `DataType` into `ShaderDataType`. Resolve to [#46](https://github.com/compas-dev/compas_viewer/issues/46).
* Added `ViewerScene` as an attribute of the `Viewer` class. resolve [#28](https://github.com/compas-dev/compas_viewer/issues/28).
* Bug fix of [#73](https://github.com/compas-dev/compas_viewer/issues/73).
* Improved argument passing mechanism in the `Slider` class. Close [#76](https://github.com/compas-dev/compas_viewer/issues/76).
* Documentation images and code correction.
* Improved typing hints of `CollectionObject`.
* Changed to the point object is `show_points = True` by default. Refer to [#73](https://github.com/compas-dev/compas_viewer/issues/73).
* Changed from `super(__t, __obj)` to `super()` as the new version.
* Temporarily removed `rgba` which is causing blank screen for macos.
* Re-enabled `rgba` support by switching to `vec4` for color attributes in shader.
* Fixed the bug of missing `item` parameter in the `Viewer.add` method.
* Fixed tag text spacing and alignment issue.
* Fixed mouse selection flickering issue.
* Fixed the issue of zoom on mac.

### Removed
* Removed `utilities` folder.

## [1.0.1] 2024-02-01

### Added

### Changed

* Fixed the bug to include `data` folder in the package.

### Removed


## [1.0.0] 2024-02-01

### Added
* Added examples in the doc.
* Added `Treeform`.
* Added basic layout elements: `MenubarLayout`, `ToolbarLayout`, `StatusbarLayout`,`SidedockLayout`.
* Added Actions: delete_selected, camera_info, selection_info.
* Added basic buildup of `Layout`'s configurations. The .json template and the configuration classes.
* `Layout` class basic buildup: `Layout`, `ViewportLayout`, `WindowLayout`.
* Added terminal activation of the viewer.
* Added `PyOpenGL_accelerate` dependency.
* Added repo images. 
* Added `installation` documentation.
* Added documentations: index, api, etc. Mockups style is improved.
* Added `DeleteSelected` action class.
* Added `ShaderDataType` as the data type template for generating the buffer.
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

* Fixed [#64](https://github.com/compas-dev/compas_viewer/issues/64).
* Patch github actions.
* Fix [#63](https://github.com/compas-dev/compas_viewer/issues/63). 
* Updated the configuration architecture.
* Updated the `delete_selected` action.
* Renamed `NetworkObject` to `GraphObject`. See commit: https://github.com/compas-dev/compas/commit/7f7098c11a1a4c3c8c0b527c8f610d10adbba1a6#diff-4e906e478c68aaee46648b7323ed68106084e647748b4e0bcb5fd440c3e162fb.
* Updated the `Slider`.
* Documentation improved.
* `Timer` is moved to utilities.
* Updated `BRepObject` to connect the latest OCC package, close [#48](https://github.com/compas-dev/compas_viewer/issues/48).
* Fixed opacity bug in shaded mode.
* Fixed main page link.
* Fixed issue [#17](https://github.com/compas-dev/compas_viewer/issues/17) and avoid using `vertex_xyz`.
* Update the dependency of `compas`.
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
