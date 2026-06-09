from PySide6 import QtWidgets, QtCore

from ui_inspector import Ui_Inspector


class Inspector(QtWidgets.QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_Inspector()

        self.ui.setupUi(self)

        # Tool button group
        self.tool_group = QtWidgets.QButtonGroup(self)
        self.tool_group.setExclusive(True)

        # Add the actuall buttons from the UI file
        self.tool_group.addButton(self.ui.selectBtn, 0)
        self.tool_group.addButton(self.ui.lineBtn, 1)
        self.tool_group.addButton(self.ui.textBtn, 2)
        self.tool_group.addButton(self.ui.circleBtn, 3)
        self.tool_group.addButton(self.ui.freeBtn, 4)
        self.tool_group.addButton(self.ui.smoothLineBtn, 5)

        self.setup_connections()

        # Default to the select tool
        self.ui.selectBtn.setChecked(True)

    def setup_connections(self):
        self.ui.selectBtn.toggled.connect(
            lambda checked: self.selection_tool() if checked else None
        )

        self.ui.lineBtn.toggled.connect(
            lambda checked: self.line_tool() if checked else None
        )

        self.ui.textBtn.toggled.connect(
            lambda checked: self.text_tool() if checked else None
        )

        self.ui.circleBtn.toggled.connect(
            lambda checked: self.circle_tool() if checked else None
        )

        self.ui.freeBtn.toggled.connect(
            lambda checked: self.draw_tool() if checked else None
        )

        self.ui.smoothLineBtn.toggled.connect(
            lambda checked: self.smooth_draw_tool() if checked else None
        )

    def selection_tool(self):
        print("selection tool enabled")

    def line_tool(self):
        print("line tool enabled")

    def text_tool(self):
        print("text tool enabled")

    def circle_tool(self):
        print("circle tool enabled")

    def draw_tool(self):
        print("draw tool enabled")

    def smooth_draw_tool(self):
        print("smooth draw tool enabled")
