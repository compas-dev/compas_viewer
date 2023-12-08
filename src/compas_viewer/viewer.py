from qtpy import QtGui
from qtpy import QtWidgets
from qtpy.QtCore import QCoreApplication  # type: ignore
from qtpy.QtGui import QIcon

from .components.renderer import Render


class Viewer:
    """
    The Viewer class is the main entry of `compas_viewer`. It organizes the scene and create the GUI application.
    """

    def __init__(self):
        app = QCoreApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)
        app.references = set()

        appIcon = QIcon(os.path.join(ICONS, "compas_icon_white.png"))
        app.setWindowIcon(appIcon)
        self.title = self.config["title"]
        app.setApplicationName(self.title)

    def show(self):
        pass
