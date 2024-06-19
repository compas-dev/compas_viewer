from typing import Literal
from typing import Optional

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


class LabelWidget(QtWidgets.QWidget):
    """
    A customizable QLabel widget for Qt applications, supporting text alignment and font size adjustments.

    Parameters
    ----------
    text : str
        The text to be displayed in the label.
    alignment : Literal["right", "left", "center"], optional
        The alignment of the text in the label. Defaults to "center".
    font_size : int, optional
        The font size of the text in the label. Defaults to 8.

    Attributes
    ----------
    text : str
        The text displayed in the label.
    alignment : Literal["right", "left", "center"]
        The alignment of the text in the label.
    font_size : int
        The font size of the text in the label.

    Methods
    -------
    update_minimum_size() -> None
        Updates the minimum size of the label based on the current text and font size.

    Example
    -------
    >>> label_widget = LabelWidget("Ready...", alignment="right", font_size=16)
    >>> label_widget.show()
    """

    def __init__(self, text: str, alignment: Literal["right", "left", "center"] = "center", font_size: Optional[int] = 8):
        super().__init__()

        self.label = QtWidgets.QLabel(self)

        self.text = text
        self.font_size = font_size
        self.alignment = alignment

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.update_minimum_size()

    @property
    def default_layout(self):
        if self._default_layout is None:
            from compas_viewer.components.layout import DefaultLayout

            self._default_layout = DefaultLayout(QtWidgets.QHBoxLayout()).get_layout()
        return self._default_layout

    @property
    def text(self):
        return self.label.text()

    @text.setter
    def text(self, value: str):
        self.label.setText(value)

    @property
    def alignment(self):
        return self.label.alignment()

    @alignment.setter
    def alignment(self, value: str):
        alignments = {
            "right": QtCore.Qt.AlignRight,
            "left": QtCore.Qt.AlignLeft,
            "center": QtCore.Qt.AlignCenter,
        }
        self.label.setAlignment(alignments[value])

    @property
    def font_size(self):
        return self.label.font().pointSize()

    @font_size.setter
    def font_size(self, value: int):
        font = self.label.font()
        font.setPointSize(value)
        self.label.setFont(font)

    def update_minimum_size(self):
        font_metrics = QtGui.QFontMetrics(self.label.font())
        text_width = font_metrics.horizontalAdvance(self.label.text())
        text_height = font_metrics.height()
        self.label.setMinimumSize(text_width, text_height)
