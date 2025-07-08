from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget
from qtconsole.inprocess import QtInProcessKernelManager
from qtconsole.rich_jupyter_widget import RichJupyterWidget

from compas.geometry import Box
from compas.geometry import Frame
from compas_viewer import Viewer


class ConsoleWindow(QWidget):
    """
    A separate, top-level window that contains an IPython console.
    """

    def __init__(self, namespace=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IPython Console")
        self.resize(600, 400)

        # 1. Create the In-Process Kernel
        kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()

        # 2. Create the console widget
        kernel_client = kernel_manager.client()
        kernel_client.start_channels()
        console_widget = RichJupyterWidget()
        console_widget.kernel_manager = kernel_manager
        console_widget.kernel_client = kernel_client

        # 3. Push initial variables into the kernel's namespace
        if namespace:
            kernel_manager.kernel.shell.push(namespace)

        # 4. Set up the layout for this window
        layout = QVBoxLayout(self)
        layout.addWidget(console_widget)
        self.setLayout(layout)

        print("\nIPython console launched in a separate window.")
        print("Use the 'viewer' variable to interact with the scene.")


# --- Main execution block ---
if __name__ == "__main__":
    viewer = Viewer(show_grid=True)
    box = Box(frame=Frame.worldXY())
    viewer.scene.add(box, name="MyBox")

    # define the namespace to share with the console
    shared_namespace = {
        "viewer": viewer,
        "box": box,
        "app": viewer.app,  # The QApplication instance
        # You can add other useful imports here
        "Box": Box,
        "Frame": Frame,
    }

    # create the separate console window
    console_window = ConsoleWindow(namespace=shared_namespace)

    # only show the console window after the viewer rendering loop is started
    # QTimer.singleShot is used to post the call to the `show` method after
    # the event loop started
    QTimer.singleShot(0, console_window.show)

    viewer.show()
