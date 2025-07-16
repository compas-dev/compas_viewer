# UI Component System Refactoring

## Overview
Complete restructuring of the compas_viewer UI architecture to implement a modern component-based system with improved modularity and maintainability.

## Key Changes

### New Component Architecture
- Added `Component` base class with standardized `widget` attribute and `update()` method
- Added `BoundComponent` class for components bound to object attributes with automatic value synchronization
- All UI components now inherit from `Base` class for consistent structure

### Component Refactoring
- **Replaced dialogs with integrated components**: `CameraSettingsDialog` → `CameraSetting`, `ObjectSettingDialog` → `ObjectSetting`
- **Enhanced existing components**: Updated `Slider`, `TextEdit`, `Button` to use new inheritance model
- **Added new components**: `BooleanToggle`, `ColorPicker`, `NumberEdit`, `Container`, `Tabform`
- **Removed deprecated components**: `ColorComboBox`, `ComboBox`, `DoubleEdit`, `LineEdit`, `LabelWidget`

### UI Structure Improvements
- Moved components to dedicated `components/` folder
- Added `MainWindow`, `StatusBar`, `ViewPort` components
- Refactored `MenuBar`, `ToolBar`, `SideDock` to use new component system
- Updated `UI` class to use new component architecture

### Technical Improvements
- Standardized component initialization with `obj`, `attr`, `action` parameters
- Improved data binding with automatic attribute synchronization
- Enhanced container system with scrollable and splitter options
- Updated event handling and signal connections

## Impact
This refactoring provides a cleaner, more maintainable codebase with better separation of concerns and improved extensibility for future UI development. 