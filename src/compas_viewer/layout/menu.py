from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layout import Layout


class Menu:
    def __init__(self, layout: "Layout"):
        self.layout = layout

    def init(self):
        print("Menu")
