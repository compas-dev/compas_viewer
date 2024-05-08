from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from compas_viewer.layout import Treeform


# TODO(pitsai): move compas_viewer.layout Treeform to here
class TreeformComponents:
    def __init__(self) -> None:
        self.widgets = {}

    def initialize_settings(self):
        for name in dir(self):
            if name.endswith("_setting") and callable(getattr(self, name)):
                method = getattr(self, name)
                method()

    @property
    def viewer(self):
        from compas_viewer.viewer import Viewer

        return Viewer()

    def register_widget(self, name: str, widget) -> None:
        self.widgets[name] = widget

    def get_widget(self, name: str):
        return self.widgets.get(name)

    def create_setting_group(self, title: str, settings):
        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(settings)
        self.register_widget(title, splitter)

    def treeform_setting(self) -> None:
        form_ids = Treeform(self.viewer.scene, {"Name": (lambda o: o.name), "Object": (lambda o: o)})
        self.create_setting_group("TreeForm", form_ids)
