from PySide6.QtWidgets import QLabel


class LabelFactory(QLabel):
    def create_label(self) -> QLabel:
        """Create and configure a QLabel instance."""
        label = QLabel()
        # Add any additional configuration here
        return label

    def set_text(self, text: str = "default text") -> QLabel:
        label = self.create_label()
        label.setText(text)
        return label
