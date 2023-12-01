********************************************************************************
File Structure
********************************************************************************

::`compas_viewer` reads its customized ::`.viewer` file. The file architecture is designed for better data exchange, collaboration, and communication.

Concept
===========

1. **Folder-based** :  ::`.viewer` file is a `.zip` folder (archive) that contains files in various formats.

2. **Extendability** :  ::`.viewer` file could contain any type of files. The core functions of viewer are `.json` based and the invoking functions are dictionary-find based, meaning that only missing parameters will cause the loading failure while redundant parameters will only be ignored.

Quick Look
==========

.. figure::  _images/diagrams/generated/file_structure.svg
    :figclass: figure
    :class: figure-img img-fluid


Structure
=========

- **FILENAME.viewer**:  ::`.viewer` file is a `.zip` based folder that collect rich format of files ...

  - **viewer.json**: The viewer.json contains all the settings about the viewer application it self: with, height, fullscreen, ...

    - **about**: Basic info. | *str* | `"about": "Hello."`
    - **title**: The title of the viewer. | *str* | `"title": "COMPAS Viewer"`
    - **width**: The width of the viewer. | *int* | `"width": 1280`
    - **height**: The height of the viewer. | *int* | `"height ": 720`
    - **fullscreen**: Full screen option. | *bool* | `"fullscreen ": false`

  - **scene.json**: The scene.json contains all the settings about the scene: background color, grid, ...

    - **show_grid**: Show grid option. | *bool* | `"show_grid ": true`
    - **view_mode**: View mode option. | *str* | `"view_mode ": "shaded"`
    - **background_color**: Background color option. | *List* | `"background_color ": [1, 1, 1, 1]`
    - **selection_color**: Selection color option. | *List* | `"selection_color ": [1.0, 1.0, 0.0]`

  - **ui.json**: The ui.json contains all the settings about the ui: sidedock, sidebar, statusbar, ...

    - **statusbar**: The statusbar key controls the statusbar behavior. | *Dict* |

      - **texts**: Controls the text in the statusbar. | *str* | `"texts": "Ready"`
      - **show_fps**: Controls the fps status in the statusbar. | *bool* | `"show_fps": true`

    - **menubar**: The menubar key controls the menubar behavior. | *Dict* |

      - **enable_menubar**: If the menubar is displayed. false means no further menubar settings will not be applied. | *bool* | `"enable_menubar": true`
      - **items**: An *ordered List* of items as *Dictionary* to put in the menubar ... | *List[Dict]* |

        - **text**: The name displayed on the menu item. | *type* | `"text": "View"`
        - **items**: An *ordered List* of items to put inside the menu item. | *List[Dict]* |

          - **type**: The type of this group of item: "radio", "action", "separator" ... | *str* | `"type": "radio"`
          - **text**: The menu item name displayed inside the menu. | *str* | `"text": "Shaded"`
          - **action**: Function name to trigger when the menu item is clicked. | *str* | `"action": "view_shaded"`
          - **...**: Other keys depending on the type.

    - **toolbar**: The toolbar key controls the toolbar behavior. | *Dict* |

      - **enable_toolbar**: If the toolbar is displayed. false means no further toolbar settings will not be applied. | *bool* | `"enable_toolbar": true`
      - **items**: An *ordered List* of items as *Dictionary* to put in the toolbar ... | *List[Dict]* |

        - **type**: The type of this item: "action", "separator" ... | *str* | `"type": "action"`
        - **text**: The toolbar item name displayed on the toolbar. | *str* | `"text": "Capture"`
        - **action**: Function name to trigger when the toolbar item is clicked. | *str* | `"action": "view_capture"`

    - **sidebar**: The sidebar key controls the sidebar behavior. | *Dict* |

      - **enable_sidebar**: If the sidebar is displayed. false means no further sidebar settings will not be applied. | *bool* | `"enable_sidebar": true`
      - **items**: An *ordered List* of items as *Dictionary* to put in the toolbar ... | *List[Dict]* |

        - **type**: The type of this item: "checkbox", "slider", "button" ... | *str* | `"type": "checkbox"`
        - **text**: The sidebar item name displayed on the sidebar. | *str* | `"text": "Slide Point"`
        - **...**: Other keys depending on the type.

    - **sidedocks**: ::`compas_viewer` provides sidedocks as the addition to the sidebar. Every single sidedock in this *list* of dideocks follow the basic configuration rule of the sidebar | *list* |

  - **controller.json**: The controller.json contains all the settings about controlling the viewer: mouse, keys, ...

    - **mouse**:  The mouse-based control functions. The keys(functions) are fixed but items(bindings) are customizable. | *Dict* |

      - **pan**:  The pan function. | *Dict* | `{"mouse": "r", "key": "shift"}`
      - **rotate**:  The rotate function. | *Dict* | `{"mouse": "r", "key": ""}`
      - **box_selection**:  The box_selection function. | *Dict* | `{"mouse": "l", "key": ""}`
      - **box_deselection**:  The box_selection function. | *Dict* | `{"mouse": "l", "key": "control"}`
      - **selection**:  The box_selection function. | *Dict* | `{"mouse": "l", "key": ""}`
      - **multi_selection**:  The box_selection function. | *Dict* | `{"mouse": "l", "key": "shift"}`
      - **deselection**:  The box_selection function. | *Dict* | `{"mouse": "l", "key": "control"}`

    - **keys**:  The key-based control functions. Both keys and items are customizable. Extended actions put in the actions folder | *Dict* | `{"zoom_selected": ["f"],"view_top": ["control", "f1"]}`

  - **actions**: Folder for containing the extended actions.
  - **geometries.json**: The geometries.json is *dictionary* data that indicate all the geometry pointers and their relations.
  - **geometry_data.json**: The geometry_data.json contains all the geometry information ( items are parsed `compas.geometry`, directory of a geometry file inside this folder, or URL directory). This is the targets of the pointers in the geometries.json
  - **flow.json**: The flow function is a `ryven` based visual scripting tool. The documentation and development of flow will be developed later on ...
