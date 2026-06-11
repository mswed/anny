from PySide6 import QtWidgets
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor


class ColorPickerDrowpdown(QtWidgets.QMenu):
    colorSelected = Signal(tuple)

    COLORS = [
        "#FF0000",
        "#FF7700",
        "#FFFF00",
        "#00FF00",
        "#00FFFF",
        "#0000FF",
        "#FF00FF",
        "#FFFFFF",
        "#000000",
        "#888888",
        "#FF4444",
        "#4444FF",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        widget = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout(widget)
        grid.setSpacing(2)
        grid.setContentsMargins(4, 4, 4, 4)

        for i, hex_color in enumerate(self.COLORS):
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(20, 20)
            btn.setStyleSheet(f"background-color: {hex_color}; border: none;")
            btn.clicked.connect(
                lambda checked=False, c=hex_color: self._on_color_clicked(c)
            )
            grid.addWidget(btn, i // 4, i % 4)

        # Add an action to the menu
        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(widget)
        self.addAction(action)

    def _on_color_clicked(self, hex_color):
        print("recieved hex color is", hex_color)
        c = QColor(hex_color)
        print("selected color is", c)
        print("converted color is", c.redF(), c.greenF(), c.blueF(), 1.0)
        self.colorSelected.emit((c.redF(), c.greenF(), c.blueF(), 1.0))
        self.close()
