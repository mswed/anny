from PySide6 import QtWidgets, QtCore
import rv.commands as crv
from pprint import pprint

from ui_inspector import Ui_Inspector


class Inspector(QtWidgets.QDialog):
    def __init__(self, mode, parent=None) -> None:
        super().__init__(parent)
        self.mode = mode
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

        self.tool_group.idClicked.connect(self.on_tool_changed)

        # Default to the select tool
        self.ui.selectBtn.setChecked(True)

    def on_tool_changed(self, tool_id):
        self.mode.set_active_tool(tool_id)

    def selection_tool(self):
        print("selection tool enabled")

    def line_tool(self):
        print("line tool enabled")

        # We first change the event binding so RV knows what to do
        crv.bind(
            "py-anny-mode", "global", "pointer-1--push", self.draw_start, "Mouse down"
        )
        crv.bind(
            "py-anny-mode", "global", "pointer-1--drag", self.draw_update, "Mouse drag"
        )
        crv.bind(
            "py-anny-mode", "global", "pointer-1--release", self.draw_end, "Mouse up"
        )

    def text_tool(self):
        print("text tool enabled")

    def circle_tool(self):
        print("circle tool enabled")

    def draw_tool(self):
        print("draw tool enabled")

    def smooth_draw_tool(self):
        print("smooth draw tool enabled")

    def draw_start(self, event):
        print("starting draw")
        print("pointer", event.pointer())
        print("domain", event.domain())
        print("subdomain", event.subDomain())

    def draw_update(self, event):
        print("updating draw")

    def draw_end(self, event):
        print("ended draw")
