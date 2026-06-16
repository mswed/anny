from PySide6 import QtWidgets, QtCore
import rv.commands as crv
from pprint import pprint

from ui_inspector import Ui_Inspector
from style import ANNY_STYLESHEET
from color_picker import ColorPickerDrowpdown


class Inspector(QtWidgets.QDialog):
    def __init__(self, mode, parent=None) -> None:
        super().__init__(parent)
        self.mode = mode
        self.ui = Ui_Inspector()
        self.current_stroke_color = (1.0, 0.0, 0.0, 1.0)
        self.start_cap = None
        self.end_cap = None

        self.ui.setupUi(self)
        self.setStyleSheet(ANNY_STYLESHEET)

        # Tool button group
        self.tool_group = QtWidgets.QButtonGroup(self)
        self.tool_group.setExclusive(True)

        # Add the actual buttons from the UI file
        self.tool_group.addButton(self.ui.selectBtn, 0)
        self.tool_group.addButton(self.ui.lineBtn, 1)
        self.tool_group.addButton(self.ui.textBtn, 2)
        self.tool_group.addButton(self.ui.circleBtn, 3)
        self.tool_group.addButton(self.ui.freeBtn, 4)
        self.tool_group.addButton(self.ui.smoothLineBtn, 5)

        # Setup combo boxes
        self.ui.startCapCb.addItem("-", None)
        self.ui.startCapCb.addItem("<", "arrow")
        self.ui.endCapCb.addItem("-", None)
        self.ui.endCapCb.addItem(">", "arrow")

        # Connections
        self.setup_connections()

        # Default to the select tool
        self.ui.selectBtn.setChecked(True)

    def on_tool_changed(self, tool_id):
        self.mode.set_active_tool(tool_id)

    def setup_connections(self):
        self.tool_group.idClicked.connect(self.on_tool_changed)
        self.ui.strokeOpacityField.valueChanged.connect(self.mode.update_opacity)
        self.ui.strokeWidthField.valueChanged.connect(self.mode.update_width)
        self.ui.strokeColorBtn.clicked.connect(self.show_color_picker)
        self.ui.startCapCb.currentIndexChanged.connect(self.mode.update_start_cap)
        self.ui.endCapCb.currentIndexChanged.connect(self.mode.update_end_cap)

    def show_color_picker(self):
        menu = ColorPickerDrowpdown()
        menu.colorSelected.connect(self.on_color_changed)
        menu.exec(
            self.ui.strokeColorBtn.mapToGlobal(
                self.ui.strokeColorBtn.rect().bottomLeft()
            )
        )

    def on_color_changed(self, color):
        r, g, b, a = color
        # Update swatch
        self.ui.strokeColorBtn.setStyleSheet(
            f"background-color: rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, {int(a * 255)}); border: none;"
        )
        # Set the current storke color
        if self.mode.current_stroke:
            self.mode.current_stroke.color = (
                r,
                g,
                b,
                self.ui.strokeOpacityField.value(),
            )

        self.current_stroke_color = (r, g, b, a)
