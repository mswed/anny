from PySide6 import QtGui, QtWidgets, QtCore
import rv.commands as crv
from pprint import pprint

from ui_inspector import Ui_Inspector
from style import ANNY_STYLESHEET
import resources_rc
from color_picker import ColorPickerDrowpdown


class Inspector(QtWidgets.QDialog):
    def __init__(self, mode, parent=None) -> None:
        super().__init__(parent)
        self.mode = mode
        self.ui = Ui_Inspector()
        self.current_stroke_color = (1.0, 0.0, 0.0, 1.0)
        self.current_fill_color = (0.0, 0.0, 0.0, 1.0)
        self.start_cap = None
        self.end_cap = None

        self.ui.setupUi(self)
        # Set the overall style
        self.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
        # Override some settings to make it nicer
        self.setStyleSheet(ANNY_STYLESHEET)

        # Tool button group
        self.tool_group = QtWidgets.QButtonGroup(self)
        self.tool_group.setExclusive(True)

        # Add the actual buttons from the UI file and assign them IDs
        self.tool_group.addButton(self.ui.selectBtn, 0)
        self.tool_group.addButton(self.ui.freeBtn, 1)
        self.tool_group.addButton(self.ui.lineBtn, 2)
        self.tool_group.addButton(self.ui.rectBtn, 3)
        self.tool_group.addButton(self.ui.circleBtn, 4)
        self.tool_group.addButton(self.ui.textBtn, 5)

        # Setup combo boxes
        self.ui.startCapCb.addItem(QtGui.QIcon(":/icons/cap-plain.svg"), "", None)
        self.ui.startCapCb.addItem(
            QtGui.QIcon(":/icons/cap-arrow-left.svg"), "", "arrow"
        )
        self.ui.startCapCb.addItem(QtGui.QIcon(":/icons/cap-tick-left.svg"), "", "tick")
        self.ui.startCapCb.addItem(
            QtGui.QIcon(":/icons/cap-circle-left.svg"), "", "circle"
        )
        self.ui.endCapCb.addItem(QtGui.QIcon(":/icons/cap-plain.svg"), "", None)
        self.ui.endCapCb.addItem(
            QtGui.QIcon(":/icons/cap-arrow-right.svg"), "", "arrow"
        )
        self.ui.endCapCb.addItem(QtGui.QIcon(":/icons/cap-tick-right.svg"), "", "tick")
        self.ui.endCapCb.addItem(
            QtGui.QIcon(":/icons/cap-circle-right.svg"), "", "circle"
        )

        # Connections
        self.setup_connections()

        # Default to the select tool
        self.ui.selectBtn.setChecked(True)

    def closeEvent(self, arg__1: QtGui.QCloseEvent) -> None:
        self.mode.unbind()

        return super().closeEvent(arg__1)

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
        self.ui.strokeSmoothingField.valueChanged.connect(self.update_smoothing)
        self.ui.fillColorBtn.clicked.connect(self.show_color_picker)
        self.ui.fillOpacityField.valueChanged.connect(self.update_fill_opacity)

        # Text field has two connections one for updates and one for losingn focus
        self.ui.textField.textChanged.connect(self.update_text)
        self.ui.textField.editingFinished.connect(self.commit_edit)

        self.ui.fontCb.currentFontChanged.connect(self.update_font)
        self.ui.fontSizeField.valueChanged.connect(self.update_font)

        self.ui.clearFrameBtn.clicked.connect(self.clear_frame)

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
            f"background-color: rgba({int(r * 255)}, {int(g * 255)}, {int(b * 255)}, 255); border: none;"
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

            crv.redraw()

    def update_start_cap(self) -> None:
        """Update the start of line to match the start cap selection"""

        if self.mode.current_stroke:
            self.mode.current_stroke.start_cap = self.ui.startCapCb.currentData()
            crv.redraw()

    def update_end_cap(self) -> None:
        """Update the start of line to match the start cap selection"""

        if self.mode.current_stroke:
            self.mode.current_stroke.end_cap = self.ui.endCapCb.currentData()
            crv.redraw()

    def update_stroke_opacity(self) -> None:
        """Update the stroke opacity based on UI selection"""

        if self.mode.current_stroke:
            self.mode.current_stroke.opacity = float(self.ui.strokeOpacityField.value())
            crv.redraw()

    def update_smoothing(self) -> None:
        """Update the smoothing of a freehand stroke"""

        if self.mode.current_stroke:
            self.mode.current_stroke.smoothing = self.ui.strokeSmoothingField.value()
            crv.redraw()

    def update_fill_opacity(self):
        """Update the fill opacity based on UI selection"""
        if self.mode.current_stroke:
            self.mode.current_stroke.fill_opacity = float(
                self.ui.fillOpacityField.value()
            )
            crv.redraw()

    def update_stroke_width(self):
        """Update the stroke width based on UI selection"""
        if self.mode.current_stroke:
            self.mode.current_stroke.width = float(self.ui.strokeWidthField.value())
            crv.redraw()

    def update_text(self):
        """Update the text based on UI selection"""
        if (
            self.mode.current_stroke
            and "text" in self.mode.current_stroke.editable_properties
        ):
            self.mode.current_stroke.text = self.ui.textField.toPlainText()
            self.mode.current_stroke.editing = True
            crv.redraw()

    def commit_edit(self):
        """Update the editing status to False on the stroke"""
        if (
            self.mode.current_stroke
            and "text" in self.mode.current_stroke.editable_properties
        ):
            self.mode.current_stroke.editing = False
            crv.redraw()

    def update_font(self):

        if (
            self.mode.current_stroke
            and "font" in self.mode.current_stroke.editable_properties
        ):
            font = self.ui.fontCb.currentFont()
            font.setPointSize(self.ui.fontSizeField.value())

            self.mode.current_stroke.font = font

            crv.redraw()

    def clear_frame(self):
        self.mode.clear_frame()
