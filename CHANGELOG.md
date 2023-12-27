# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

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


### Changed

* Moved `gl` from `render` folder to the `utilities` folder.
* All color representations are now in `compas.colors.Color`.
* Reduce the `numpy.array` representation. Mostly use `list` instead for clarity.
* Comments improved and better type hints.

### Removed
