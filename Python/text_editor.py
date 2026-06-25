from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Signal


class TextEditWithCommit(QtWidgets.QTextEdit):
    """
    A text edit that emits a finished signal when it loses focus
    """

    editingFinished = Signal()

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:
        super().focusOutEvent(e)
        self.editingFinished.emit()
