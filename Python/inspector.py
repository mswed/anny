from PySide6 import QtWidgets, QtCore

from ui_inspector import Ui_Inspector


class Inspector(QtWidgets.QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_Inspector()

        self.ui.setupUi(self)
