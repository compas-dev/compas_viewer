import sys
from PySide6.QtWidgets import QApplication
from compas_viewer.config import Config
from compas_viewer.scene.scene import ViewerScene
from compas_viewer.ui.ui import UI

from compas_viewer.controller import Controller
from compas_viewer.configurations import ControllerConfig
from compas_viewer.components.renderer import Renderer
from compas_viewer.configurations import RendererConfig

"""
├── compas_viewer/                   
│   ├── __init__.py         # Makes app a Python package
│   ├── main.py             # Entry point of the application
│   ├── viewer.py           # Main window class
│   └── components/         # UI components like custom widgets, buttons, etc.
│       ├── __init__.py
│       ├── default_component_factory.py
│       ├── box_factory.py
│       ├── buttom_factory.py
│       ├── lable_factory.py
│       └── ...
│
├────── ui/              # UI components like custom widgets, buttons, etc.
│       ├── ui.py/
│       ├── main_window.py/
│       ├── menu.py/
│       ├── status_bar.py/
│       ├── tool_bar.py/
│       ├── view_port.py/
│       └── ...
│
├────── action/              
│       ├── 
│       ├── 
│       └── ...

"""

class Viewer():

    _instance = None  # Class-level attribute that holds the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Viewer, cls).__new__(cls)
            cls._instance.init(*args, **kwargs) 
        return cls._instance

    def init(self, *args, **kwargs):
        if not hasattr(self, 'initialized'): 
            
            if not QApplication.instance():
                self.app = QApplication(sys.argv)
            else:
                self.app = QApplication.instance()

            self.config = Config.from_json("src/compas_viewer/config.json")
            self.scene = ViewerScene(name="ViewerScene", context="Viewer")
            #TODO(pitsai): combine config file
            self.renderer = Renderer(RendererConfig.from_default())
            self.controller = Controller(ControllerConfig.from_default())
            self.ui = UI()
            self.initialized = True 

    def show(self):
        if hasattr(self, 'ui'):
            self.ui.init()
            self.ui.show()
            self.app.exec()
        else:
            print("UI component not initialized.")

