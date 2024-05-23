from typing import TYPE_CHECKING

from PySide6 import QtWidgets

if TYPE_CHECKING:
    from compas_viewer.renderer import Renderer

    from .sidebar import SideBarRight


class ViewPort:
    def __init__(self, renderer: "Renderer", sidebar: "SideBarRight"):
        self.widget = QtWidgets.QSplitter()
        self.widget.addWidget(renderer)
        self.widget.addWidget(sidebar.widget)
        self.widget.setSizes([800, 200])
