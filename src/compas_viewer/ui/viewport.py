from typing import TYPE_CHECKING

from PySide6 import QtWidgets

if TYPE_CHECKING:
    from compas_viewer.renderer import Renderer

    from .sidebar import SideBarRight
    from .ui import UI


class ViewPort:
    def __init__(self, ui: "UI", renderer: "Renderer", sidebar: "SideBarRight"):
        self.ui = ui
        self.widget = QtWidgets.QSplitter()
        self.widget.addWidget(renderer)
        self.widget.addWidget(sidebar.widget)
        self.widget.setSizes([800, 200])
