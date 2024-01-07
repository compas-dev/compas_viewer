from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .layout import Layout


class Body(Layout):


    def init(self):
        self.layout.body_layout.addWidget(self.layout.viewer.render)
        self.layout.window.setCentralWidget(self.layout.viewer.render)
