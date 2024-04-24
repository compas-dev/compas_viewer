import sys
from PySide6.QtWidgets import QApplication
from compas_viewer.config import Config
from compas_viewer.scene.scene import ViewerScene
from compas_viewer.ui.ui import UI

from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame

from compas_viewer.components.renderer import Renderer
from compas_viewer.configurations import RendererConfig
from compas_viewer.configurations import ControllerConfig
from compas_viewer.configurations import ViewerConfig
from compas_viewer.controller import Controller

class Singleton:
    _instances = {}
    
    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__new__(cls)
            # Initialize immediately upon creation, before adding to instances dictionary
            instance.init(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Viewer(Singleton):
    # def __init__(self) -> None:
    #     super().__init__()
    #     self.ui = UI(self)

    def init(self, *args, **kwargs):
        if not hasattr(self, 'initialized'):  # This check prevents reinitialization
            self.app = QApplication(sys.argv)
            self.config = Config.from_json("src/compas_viewer/config.json")
            self.scene = ViewerScene(self, name="ViewerScene", context="Viewer")
            self.ui = UI(self)
            self.initialized = True  # Mark as initialized
            print(f"Full config {self.config}")

    def show(self):
        if hasattr(self, 'ui'):
            self.ui.init()
            self.ui.show()
            self.app.exec()
        else:
            print("UI component not initialized.")


if __name__ == "__main__":
    viewer = Viewer()

    # for i in range(5):
    #     for j in range(5):
    #         viewer.scene.add(
    #             Box(0.5, 0.5, 0.5, Frame([i, j, 0], [1, 0, 0], [0, 1, 0])),
    #             show_points=False,
    #             show_lines=True,
    #             surfacecolor=Color(i / 10, j / 10, 0.0),
    #             name=f"Box_{i}_{j}",
    #         )
    #         print()
    
    viewer.show()

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