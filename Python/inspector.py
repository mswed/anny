from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt
from typing import Optional
from pathlib import Path
import rv.commands as crv

from ui_inspector import Ui_Inspector
from ui_shotgrid import Ui_Shotgrid
from style import ANNY_STYLESHEET
import resources_rc
from color_picker import ColorPickerDrowpdown


class Inspector(QtWidgets.QDialog):
    PROPERTY_WIDGETS = {
        "width": ["strokeWidthField"],
        "opacity": ["strokeOpacityField"],
        "smoothing": ["strokeSmoothingField"],
        "start_cap": ["startCapCb"],
        "end_cap": ["endCapCb"],
        "fill_opacity": ["fillOpacityField"],
        "text": ["textField", "fontCb", "fontSizeField"],
    }

    ANNOTATION_TAB = 0
    SG_TAB = 1
    SG_FORM = 0
    NO_SG = 1

    def __init__(self, mode, parent=None) -> None:
        super().__init__(parent)
        self.mode = mode
        # We request an update on init (if sg is available)
        self.sg_update_requested = True

        # Set up tab system
        layout = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tabs)

        # --- Annotations Tab ---
        annotation_widget = QtWidgets.QWidget()
        self.ui = Ui_Inspector()
        self.ui.setupUi(annotation_widget)
        self.tabs.addTab(annotation_widget, "Annotate")
        self.current_stroke_color = (1.0, 0.0, 0.0, 1.0)
        self.current_fill_color = (0.0, 0.0, 0.0, 1.0)
        self.start_cap = None
        self.end_cap = None

        # --- Shotgrid Tab ---
        sg_widget = QtWidgets.QWidget()
        self.sg_ui = Ui_Shotgrid()
        self.sg_ui.setupUi(sg_widget)
        self.tabs.addTab(sg_widget, "ShotGrid Note")

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
        self._setup_connections()

        # Default to the select tool
        self.ui.selectBtn.setChecked(True)
        self.resize(380, 660)

    def _setup_connections(self) -> None:
        """Connect UI to actions"""

        self.tool_group.idClicked.connect(self._on_tool_changed)
        self.ui.strokeWidthField.valueChanged.connect(self._update_stroke_width)
        self.ui.strokeOpacityField.valueChanged.connect(self._update_stroke_opacity)
        self.ui.strokeColorBtn.clicked.connect(self._show_color_picker)
        self.ui.startCapCb.currentIndexChanged.connect(self._update_start_cap)
        self.ui.endCapCb.currentIndexChanged.connect(self._update_end_cap)
        self.ui.strokeSmoothingField.valueChanged.connect(self._update_stroke_smoothing)
        self.ui.fillColorBtn.clicked.connect(self._show_color_picker)
        self.ui.fillOpacityField.valueChanged.connect(self._update_fill_opacity)

        # Text field has two connections one for updates and one for losing focus
        self.ui.textField.textChanged.connect(self._update_text)
        self.ui.textField.editingFinished.connect(self._commit_edit)

        self.ui.fontCb.currentFontChanged.connect(self._update_font)
        self.ui.fontSizeField.valueChanged.connect(self._update_font)

        self.ui.clearFrameBtn.clicked.connect(self._clear_frame)

        # SG integration
        self.sg_ui.submitBtn.clicked.connect(self._submit_note_to_sg)

    # --- OVERRIDES ---

    def closeEvent(self, arg__1: QtGui.QCloseEvent) -> None:
        """When the inspector closes we release Anny's bindings

        Parameters
        ----------
        arg__1 : QtGui.QCloseEvent
            The close event

        Returns
        -------
        None
            The return value from the default Qt close event
        """
        self.mode.unbind()

        return super().closeEvent(arg__1)

    # --- PUBLIC API ---

    def get_save_path(self, save_type="file") -> Optional[Path]:
        dialog = QtWidgets.QFileDialog(self, "Export Annotation", str(Path.home()))
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        if save_type == "file":
            dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
            dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        else:
            dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setNameFilter("Images (*.jpg *.png)")

        if dialog.exec():
            files = dialog.selectedFiles()
            return Path(files[0]) if files else None

    def show_message(self, message, message_type="information"):
        if message_type == "information":
            QtWidgets.QMessageBox.information(self, "Info!", message)
        if message_type == "warning":
            QtWidgets.QMessageBox.warning(self, "Error!", message)
        elif message_type == "critical":
            QtWidgets.QMessageBox.critical(self, "Error!", message)

    def set_sg_tab_visibility(self, status: bool) -> None:
        """Hide or show the Shotgrid tab

        Parameters
        ----------
        status : bool
            True of showing the tab False otherwise

        """
        self.tabs.setTabVisible(self.SG_TAB, status)

    def show_sg_unavailable(self):
        self.sg_ui.sgStackedWidget.setCurrentIndex(1)

    def update_sg_data(self, data):
        self._update_version_data(
            data["entity_name"],
            data["version_name"],
            data["artist_name"],
            data["version_status"],
            data["status_list"],
        )

        # Create the subject line
        user_first_name = data["current_user"].get("name", "Unknown").split(" ")[0]
        self._update_note_subject(user_first_name, data["version_name"])

        # Update the dropdown lists and multiselection fields
        self._update_note_options(data["users"], data["tags"], data["note_types"])

    def clear_note(self):
        self.sg_ui.subjectField.clear()
        self.sg_ui.textField.clear()
        self.sg_ui.toMs.clear()
        self.sg_ui.ccMs.clear()

    def _update_note_subject(self, user_first_name, version_name):
        subject = f"{user_first_name}'s note on {version_name}"
        self.sg_ui.subjectField.setText(subject)

    def _update_version_data(
        self,
        entity_name: str,
        version_name: str,
        artist_name: str,
        status: str,
        status_list: list,
    ):
        """Update the UI with data from the SG version

        Parameters
        ----------
        entity_name : str
            The type of the entity the version was created against (Shot or Asset for now)
        version_name : str
            The namge of the SG version
        artist_name : str
            The name of the artist who created the version
        status : str
            The status of the SG version
        status_list : list
            List of available version statuses (these can change per project)

        """
        self.sg_ui.entityNameLabel.setText(entity_name)
        self.sg_ui.versionNameLabel.setText(version_name)
        self.sg_ui.artistNameLabel.setText(artist_name)
        self.sg_ui.statusCb.clear()
        if status_list:
            for i in status_list:
                code = i[0]
                name = i[1]
                self.sg_ui.statusCb.addItem(f"{code} - {name}", code)
            self.sg_ui.statusCb.setCurrentIndex(self.sg_ui.statusCb.findData(status))

    def _update_note_options(
        self, users: list, tags: list, note_types: list[str]
    ) -> None:
        """Update multiselect and dropdown options for the SG note

        Parameters
        ----------
        users : list
            List of active SG users and groups
        tags : list
           List of SG tags
        note_types : list[str]
            List of SG node types

        """
        if not self.sg_update_requested:
            # We should be using the cached list
            return

        icons = {
            "HumanUser": ":/icons/user-solid-full.svg",
            "Group": ":/icons/user-group-solid-full.svg",
            "Tag": ":/icons/hashtag-solid-full.svg",
        }

        # Clear existing options
        self.sg_ui.toMs.clear()
        self.sg_ui.ccMs.clear()
        self.sg_ui.tagsMs.clear()
        self.sg_ui.noteTypeCb.clear()

        # Configure multiselects
        self.sg_ui.toMs.configure(
            model=users,
            record_name=self.display_name,
            record_id=self.record_id,
            record_type="type",
            icons=icons,
            placeholder="Who MUST know about this note?",
        )

        self.sg_ui.ccMs.configure(
            model=users,
            record_name=self.display_name,
            record_id=self.record_id,
            record_type="type",
            icons=icons,
            placeholder="Who should know about this note?",
        )

        self.sg_ui.tagsMs.configure(
            model=tags,
            record_name="name",
            record_id="id",
            record_type="type",
            icons=icons,
            placeholder="Add some tags!",
        )

        # Set up combobox
        if note_types:
            for t in note_types:
                self.sg_ui.noteTypeCb.addItem(t)

        # Mark the cache as current
        self.sg_update_requested = False

    # --- EVENT HANDLERS ---

    def _on_tab_changed(self, tab: int) -> None:
        """If we switch to the Shotgrid tab we update the UI with the version data

        Parameters
        ----------
        tab : int
            The tab we're switching to
        """
        if tab == self.SG_TAB:
            self.sg_ui.sgStackedWidget.setCurrentIndex(0)
            self.mode.try_sg_refresh()

    def _on_tool_changed(self, tool_id: int):
        """Select the active tool and change to cursor to match it

        Parameters
        ----------
        tool_id : int
            Tool button ID
        """
        self.mode.set_active_tool(tool_id)
        if tool_id == 0:
            crv.setCursor(Qt.CursorShape.ArrowCursor.value)
        else:
            crv.setCursor(Qt.CursorShape.CrossCursor.value)

    def _on_color_changed(self, color: tuple, sender: QtWidgets.QPushButton, kind: str):
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

    # --- SLOTS ---
    def _show_color_picker(self):
        """Show our custom color picker for the stroke or fill color"""

        sender = self.sender()
        kind = "stroke" if sender == self.ui.strokeColorBtn else "fill"
        menu = ColorPickerDrowpdown()
        menu.colorSelected.connect(
            lambda color: self._on_color_changed(color, sender=sender, kind=kind)
        )
        menu.exec(sender.mapToGlobal(sender.rect().bottomLeft()))

    def _update_stroke_width(self):
        """Update the stroke width based on UI selection"""
        if self.mode.current_stroke:
            self.mode.current_stroke.width = float(self.ui.strokeWidthField.value())
            crv.redraw()

    def _update_stroke_opacity(self) -> None:
        """Update the stroke opacity based on UI selection"""

        if self.mode.current_stroke:
            self.mode.current_stroke.opacity = float(self.ui.strokeOpacityField.value())
            crv.redraw()

    def _update_stroke_smoothing(self) -> None:
        """Update the smoothing of a freehand stroke"""

        if self.mode.current_stroke:
            self.mode.current_stroke.smoothing = self.ui.strokeSmoothingField.value()
            crv.redraw()

    def _update_start_cap(self) -> None:
        """Update the start of line to match the start cap selection"""

        if self.mode.current_stroke:
            self.mode.current_stroke.start_cap = self.ui.startCapCb.currentData()
            crv.redraw()

    def _update_end_cap(self) -> None:
        """Update the start of line to match the start cap selection"""

        if self.mode.current_stroke:
            self.mode.current_stroke.end_cap = self.ui.endCapCb.currentData()
            crv.redraw()

    def _update_fill_opacity(self):
        """Update the fill opacity based on UI selection"""
        if self.mode.current_stroke:
            self.mode.current_stroke.fill_opacity = float(
                self.ui.fillOpacityField.value()
            )
            crv.redraw()

    def _update_text(self):
        """Update the text based on UI selection"""
        if (
            self.mode.current_stroke
            and "text" in self.mode.current_stroke.editable_properties
        ):
            self.mode.current_stroke.text = self.ui.textField.toPlainText()
            self.mode.current_stroke.editing = True
            crv.redraw()

    def _commit_edit(self):
        """Update the editing status to False on the stroke"""
        if (
            self.mode.current_stroke
            and "text" in self.mode.current_stroke.editable_properties
        ):
            self.mode.current_stroke.editing = False
            crv.redraw()

    def _update_font(self):
        """Update font and font size"""

        if (
            self.mode.current_stroke
            and "font" in self.mode.current_stroke.editable_properties
        ):
            font = self.ui.fontCb.currentFont()
            font.setPointSize(self.ui.fontSizeField.value())

            self.mode.current_stroke.font = font

            crv.redraw()

    def _clear_frame(self):
        """Delete all annotations on the frame"""
        self.mode.clear_frame()

    def _submit_note_to_sg(self):
        """Submit a note to SG"""

        self.mode.create_sg_note_and_upload()

    # --- HELPERS ---
    @staticmethod
    def display_name(data):
        if data.get("type") == "HumanUser":
            return f"{data['name']} ({data['login']})"
        else:
            return data["code"]

    @staticmethod
    def record_id(data):
        return f"{data['id']}-{data['type']}"
