import sys

from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QDate
from PySide6.QtCore import QDateTime
from PySide6.QtCore import QLocale
from PySide6.QtCore import QMetaObject
from PySide6.QtCore import QObject
from PySide6.QtCore import QPoint
from PySide6.QtCore import QRect
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt
from PySide6.QtCore import QTime
from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction
from PySide6.QtGui import QBrush
from PySide6.QtGui import QColor
from PySide6.QtGui import QConicalGradient
from PySide6.QtGui import QCursor
from PySide6.QtGui import QFont
from PySide6.QtGui import QFontDatabase
from PySide6.QtGui import QGradient
from PySide6.QtGui import QIcon
from PySide6.QtGui import QImage
from PySide6.QtGui import QKeySequence
from PySide6.QtGui import QLinearGradient
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPalette
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QRadialGradient
from PySide6.QtGui import QTransform
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QDockWidget
from PySide6.QtWidgets import QGridLayout
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QMenuBar
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtWidgets import QStatusBar
from PySide6.QtWidgets import QTabWidget
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QWidget

from .layout import Layout


class BasicLayout(Layout):
    window_layout: QVBoxLayout



    def define_statusbar(self):
        """Define the status bar of the window."""
        self.statusbar.addWidget(QLabel(self.config.statusbar), 1)

        if self.config.show_fps:
            self._fps = QLabel(f"fps: ")
            self.statusbar.addWidget(self._fps)

    def define_menubar(self):
        """Define the menu bar of the window."""
        menu_files = QMenu(self.menubar)
        menu_files.setTitle("File")
        # self.menubar.addAction(menu_files.menuAction())
        self.menubar.addMenu(menu_files)

        menu_about = QMenu(self.menubar)
        menu_about.setTitle("About")
        # self.menubar.addAction(menu_about.menuAction())
        self.menubar.addMenu(menu_about)

        menu_others = QMenu(self.menubar)
        menu_others.setTitle("Others")
        # self.menubar.addAction(menu_others.menuAction())
        self.menubar.addMenu(menu_others)

        def define_menubar_file(menu_files: QMenu):
            save_as = QAction(self.window)
            save_as.setText("Save As...")
            menu_files.addAction(save_as)

        define_menubar_file(menu_files)
        # menu_files.addAction(self.import_configurations)
        # menu_files.addSeparator()
        # menu_files.addAction(self.export_geometries)
        # menu_files.addAction(self.export_configurations)
        # menu_files.addAction(self.export_all)
        # menu_files.addSeparator()
        # menu_about.addAction(self.compas)
        # menu_about.addAction(self.compas_viewer)
        # menu_about.addAction(self.compas_association)

    # def define_toolbar(self):
    #     """Define the toolbar of the window."""
    #     self.action_new = QAction(self.window)
    #     self.action_new.setObjectName("New")

    #     self.action_open = QAction(self.window)
    #     self.action_open.setObjectName("Open")

    #     self.save_as.setObjectName("Save As")

    #     self.import_configurations = QAction(self.window)
    #     self.import_configurations.setObjectName("Import Configurations")

    #     self.export_geometries = QAction(self.window)
    #     self.export_geometries.setObjectName("Export Geometries")

    #     self.export_configurations = QAction(self.window)
    #     self.export_configurations.setObjectName("Export Configurations")

    #     self.export_all = QAction(self.window)
    #     self.export_all.setObjectName("Export All")

    #     self.compas = QAction(self.window)
    #     self.compas.setObjectName("COMPAS")

    #     self.compas_viewer = QAction(self.window)
    #     self.compas_viewer.setObjectName("COMPAS_Viewer")

    #     self.compas_association = QAction(self.window)
    #     self.compas_association.setObjectName("COMPAS_Association")

    # def define_tab(self):
    #     """Define the tab widget of the window."""
    #     self.tab_widget = QTabWidget(self.central_widget)
    #     self.tab_widget.setObjectName("Tab Widget")

    #     size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    #     size_policy.setHorizontalStretch(0)
    #     size_policy.setVerticalStretch(0)
    #     size_policy.setHeightForWidth(self.tab_widget.sizePolicy().hasHeightForWidth())

    #     self.tab_widget.setSizePolicy(size_policy)
    #     self.tab_widget.setMaximumSize(QSize(200000, 50))
    #     self.tab_1 = QWidget()
    #     self.tab_1.setObjectName("Standard")
    #     self.tab_1.setEnabled(True)
    #     self.tab_widget.addTab(self.tab_1, "")
    #     self.tab_2 = QWidget()
    #     self.tab_2.setObjectName("View")
    #     self.tab_widget.addTab(self.tab_2, "")

    #     self.vertical_layout.addWidget(self.tab_widget)



    # def define_dock(self):
    #     """Define the dock widget of the window."""
    #     self.dockWidget = QDockWidget(self.window)
    #     self.dockWidget.setObjectName("dockWidget")

    #     self.dockWidgetContents = QWidget()
    #     self.dockWidgetContents.setObjectName("dockWidgetContents")

    #     self.dockWidget.setWidget(self.dockWidgetContents)

    #     self.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dockWidget)

    #     self.tab_widget.setCurrentIndex(0)

    #     QMetaObject.connectSlotsByName(self.window)

    # def retranslateUi(self, MainWindow):

    #     self.actionOpen.setText(QCoreApplication.translate("MainWindow", "Open...", None))
    #     self.actionSave_As.setText(QCoreApplication.translate("MainWindow", "Import Geometries...", None))
    #     self.actionImport_Configurations.setText(
    #         QCoreApplication.translate("MainWindow", "Import Configurations...", None)
    #     )
    #     self.actionExport_Geometries.setText(QCoreApplication.translate("MainWindow", "Export Geometries...", None))
    #     self.actionExport_Configurations.setText(
    #         QCoreApplication.translate("MainWindow", "Export Configurations...", None)
    #     )
    #     self.actionExport_All.setText(QCoreApplication.translate("MainWindow", "Export All...", None))
    #     self.actionCOMPAS.setText(QCoreApplication.translate("MainWindow", "COMPAS Framework", None))
    #     self.actionCOMPAS_viewer.setText(QCoreApplication.translate("MainWindow", "COMPAS Viewer", None))
    #     self.actionCOMPAS_Association.setText(QCoreApplication.translate("MainWindow", "COMPAS Association", None))
    #     self.tab_widget.setTabText(
    #         self.tab_widget.indexOf(self.Standard), QCoreApplication.translate("MainWindow", "Standard", None)
    #     )
    #     self.tab_widget.setTabText(
    #         self.tab_widget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", "View", None)
    #     )
    #     # if QT_CONFIG(tooltip)
    #     self.menuFiles.setToolTip(QCoreApplication.translate("MainWindow", "Name", None))
    #     # endif // QT_CONFIG(tooltip)
    #     self.menuFiles.setTitle(QCoreApplication.translate("MainWindow", "File", None))
    #     self.menuAbout.setTitle(QCoreApplication.translate("MainWindow", "About", None))
    #     self.menuOthers.setTitle(QCoreApplication.translate("MainWindow", "Others", None))
