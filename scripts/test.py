from PySide6 import QtWidgets

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parent Widget Example")
        
        # Create a QLabel with no parent (top-level widget)
        top_level_label = QtWidgets.QLabel("Top-level QLabel (No Parent)")
        self.setCentralWidget(top_level_label)  # Set as central widget

        # Create a QLabel with this QMainWindow as parent
        child_label = QtWidgets.QLabel("Child QLabel (Parent: MyWindow)")
        self.statusBar().addWidget(child_label)  # Add to status bar

def main():
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()