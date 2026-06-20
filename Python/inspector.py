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
        self.current_fill_color = (1.0, 0.0, 0.0, 1.0)
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
        self.ui.startCapCb.addItem("|", "tick")
        self.ui.startCapCb.addItem("*", "circle")
        self.ui.endCapCb.addItem("-", None)
        self.ui.endCapCb.addItem(">", "arrow")
        self.ui.endCapCb.addItem("|", "tick")
        self.ui.endCapCb.addItem("*", "circle")

        # Connections
        self.setup_connections()

        # Default to the select tool
        self.ui.selectBtn.setChecked(True)

    def on_tool_changed(self, tool_id):
        self.mode.set_active_tool(tool_id)

    def setup_connections(self) -> None:
        """Connect UI to actions"""

        self.tool_group.idClicked.connect(self.on_tool_changed)
        self.ui.strokeWidthField.valueChanged.connect(self.update_stroke_width)
        self.ui.strokeOpacityField.valueChanged.connect(self.update_stroke_opacity)
        self.ui.strokeColorBtn.clicked.connect(self.show_color_picker)
        self.ui.startCapCb.currentIndexChanged.connect(self.update_start_cap)
        self.ui.endCapCb.currentIndexChanged.connect(self.update_end_cap)
        self.ui.fillColorBtn.clicked.connect(self.show_color_picker)
        self.ui.fillOpacityField.valueChanged.connect(self.update_fill_opacity)
        self.ui.textField.textChanged.connect(self.update_text)

    def show_color_picker(self):
        # We have more thatn one color selector, figure out which was clicked
        sender = self.sender()
        kind = "stroke" if sender == self.ui.strokeColorBtn else "fill"
        menu = ColorPickerDrowpdown()
        menu.colorSelected.connect(
            lambda color: self.on_color_changed(color, sender=sender, kind=kind)
        )
        menu.exec(sender.mapToGlobal(sender.rect().bottomLeft()))

    def on_color_changed(self, color: tuple, sender: QtWidgets.QPushButton, kind: str):
        """Update the color swatch, the color of future strokes and/or the color of the currently
        selected stroke

        Parameters
        ----------
        color : tuple
            The selected color
        sender : QtWidgets.QPushButton
            The color picker button
        kind : str
            The color to update, stroke or fill

        """
        r, g, b, a = color

        # Update swatch. Note we need to convert to an 8 bit integer
        sender.setStyleSheet(
            f"background-color: rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, {int(a * 255)}); border: none;"
        )

        # Update the inspector for any future paint event
        if kind == "stroke":
            self.current_stroke_color = (r, g, b, a)
        else:
            self.current_fill_color = (r, g, b, a)

        if self.mode.current_stroke:
            # We need to update an existing stroke
            opacity_field = (
                self.ui.strokeOpacityField
                if kind == "stroke"
                else self.ui.fillOpacityField
            )
            new_color = (r, g, b, opacity_field.value())

            if kind == "stroke":
                self.mode.current_stroke.color = new_color
            else:
                self.mode.current_stroke.fill_color = new_color

    def update_start_cap(self) -> None:
        """Update the start of line to match the start cap selection"""

        if self.mode.current_stroke:
            self.mode.current_stroke.start_cap = self.ui.startCapCb.currentData()

    def update_end_cap(self) -> None:
        """Update the start of line to match the start cap selection"""

        if self.mode.current_stroke:
            self.mode.current_stroke.end_cap = self.ui.endCapCb.currentData()

    def update_stroke_opacity(self) -> None:
        """Update the stroke opacity based on UI selection"""

        if self.mode.current_stroke:
            self.mode.current_stroke.opacity = float(self.ui.strokeOpacityField.value())

    def update_fill_opacity(self):
        """Update the fill opacity based on UI selection"""
        if self.mode.current_stroke:
            self.mode.current_stroke.fill_opacity = float(
                self.ui.fillOpacityField.value()
            )

    def update_stroke_width(self):
        """Update the stroke width based on UI selection"""
        if self.mode.current_stroke:
            self.mode.current_stroke.width = float(self.ui.strokeWidthField.value())

    def update_text(self):
        """Update the text based on UI selection"""
        if self.mode.current_stroke:
            self.mode.current_stroke.text = self.ui.textField.toPlainText()
