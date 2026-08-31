from typing import Callable, Optional, Any
from PySide6.QtCore import QEvent, QModelIndex, QTimer, Qt, QObject
from PySide6.QtGui import QStandardItem, QStandardItemModel, QResizeEvent
from PySide6.QtWidgets import QCompleter, QLineEdit, QSizePolicy, QWidget
from flowLayout import FlowLayout
from pill_badge import PillBadge


class MultiSelect(QWidget):
    """Multiselect widget that allows us to search a dropdown list of records, then create and
    remove the selection in form of a pill. To create multiselect we first need to call the class
    then run its configure function to pass it all the data it needs

    """

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent)
        self._record_name_fn = str
        self._record_id_fn = lambda x: None
        self._record_type_fn = lambda x: None
        self._icons = None
        self._build_ui()

    def configure(
        self,
        model: list,
        record_name: str | Callable,
        record_id: str | Callable,
        record_type: str | Callable,
        icons: Optional[dict] = None,
        placeholder: str = "Search people and groups",
    ):
        """Configure the widget

        Parameters
        ----------
        model : list
            The model containing the records
        record_name : str | Callable
            The callback that grabs the record name from the model, can be either a function of just the key if data is a dict
        record_id : str | Callable
            The callback that grabs the record id from the model, can be either a function of just the key if data is a dict
        record_type : str | Callable
            The callback that grabs the record type from the model, can be either a function of just the key if data is a dict
        icons : Optional[dict]
            Optional icon mapping between the record type and its icon
        placeholder : str
            The placeholder text for the search field

        """
        self._record_name_fn = self._as_accessor(record_name)
        self._record_id_fn = self._as_accessor(record_id)
        self._record_type_fn = self._as_accessor(record_type)
        self._icons = icons
        self.placeholder = placeholder
        self._set_placeholder()
        self._populate_model(model)

    def clear(self):
        """Clear the widget from all selection"""
        self._completer_model.clear()
        pills = []
        for i in range(self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            if item is not None:
                w = item.widget()
                if isinstance(w, PillBadge):
                    pills.append(w)
        for pill in pills:
            self._remove_pill(pill)

    def selected_data(self) -> list:
        """Grab the current pill data from the widget

        Returns
        -------
        list
            list of pill data
        """
        result = []
        for i in range(self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            if item is not None:
                w = item.widget()
                if isinstance(w, PillBadge):
                    result.append(w.pill_data)

        return result

    def _populate_model(self, model: list):
        """Put our model inside the completer model so we can auto complete

        Parameters
        ----------
        model : list
            The widgets original model

        """
        self._completer_model.clear()
        # Guard against an empty model
        model = model or []
        for record in model:
            item = self._create_record(record)
            self._completer_model.appendRow(item)

    def _build_ui(self):
        """Create the UI layout"""

        self.setObjectName("MultiSelect")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            #MultiSelect {
                background-color: #262220;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        # To avoid a changing field height we set the minimum
        # height to the height of a single pill + the margins
        self.setMinimumHeight(24 + 8)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.main_layout = FlowLayout(self)
        self.main_layout.setContentsMargins(6, 4, 6, 4)
        self.text_field = QLineEdit()
        # For now we match the pills height so things look right
        # TODO: If we reach a library stage we need to fix the way the layout
        # TODO: places items so they can be centered vertically
        self.text_field.setFixedHeight(24)
        self.text_field.setMinimumWidth(10)
        self._completer_model = QStandardItemModel(self)
        self.completer = QCompleter(self._completer_model, self)
        self.completer.popup().installEventFilter(self)
        self._setup_selection_box()

        self.main_layout.addWidget(self.text_field)
        self.main_layout.stretch_widget = self.text_field

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Place the dropdown on the text field (which changes size as pills are added)

        Parameters
        ----------
        watched : QObject
            The object that was clicked
        event : QEvent
            The type of the event (we are looking for Show)

        Returns
        -------
        bool
            Returns the base result so the event continues to process normally

        """
        # An event filter to snap the dropdown menu into place
        if watched is self.completer.popup() and event.type() == QEvent.Type.Show:
            # We are showing the drop down, re-position
            global_pos = self.mapToGlobal(self.rect().bottomLeft())
            dropdown = self.completer.popup()
            if dropdown:
                dropdown.move(global_pos)
                # Make sure it's the same width as the widget so it looks right
                dropdown.setFixedWidth(self.width())

        return super().eventFilter(watched, event)

    def _create_record(self, data: dict) -> QStandardItem:
        """Create a record in our completer model

        Parameters
        ----------
        data : dict
            The record data

        Returns
        -------
        QStandardItem
            The item to add to the model
        """
        display = self._record_name_fn(data)
        item = QStandardItem(display)
        item.setData(data, Qt.UserRole)
        return item

    def _restore_record(self, data: dict):
        """Records are removed from the completer model when a pill is created, so we need a way to bring them back
        when a pill is removed

        Parameters
        ----------
        data : dict
            The record data

        """
        item = self._create_record(data)
        self._completer_model.appendRow(item)

    def _on_selected(self, index: int):
        """When we select an item from the dropdown, create a pill, and remove the item from the model

        Parameters
        ----------
        index : int
            The index of the selected item in the completer model
        """
        # Map back to the unfiltered model
        source_idx = self.completer.completionModel().mapToSource(index)

        # Collect the info we need
        record = source_idx.data(Qt.DisplayRole)
        record_data = source_idx.data(Qt.UserRole)
        record_id = self._record_id_fn(record_data)

        # Create and insert the pill
        pill = self._create_pill(record, record_data)
        position = self.main_layout.count() - 1
        self.main_layout.insertWidget(position, pill)

        # Remove the record from the model
        self._remove_record(record_id)

        # Use a timer to clear the field once we're done
        QTimer.singleShot(0, self._set_placeholder)

    def _set_placeholder(self):
        """Set the text field placeholder"""

        self.text_field.clear()
        if self.main_layout.count() == 1:
            self.text_field.setPlaceholderText(self.placeholder)
        else:
            self.text_field.setPlaceholderText("")

    def _create_pill(self, text: str, data: Any) -> PillBadge:
        """Create a pill

        Parameters
        ----------
        text : str
            The pill's text
        data : Any
            The record data, this can be anything, which is why we need to register the record type
            callback

        Returns
        -------
        PillBadge
            The pill class
        """

        record_type = self._record_type_fn(data)

        icon = None
        if self._icons is not None:
            icon = self._icons.get(record_type)

        pill = PillBadge(text, icon, data=data)
        pill.deleteRequested.connect(self._remove_pill)

        return pill

    def _remove_record(self, target_id: Any):
        """Remove a record from the completer model

        Parameters
        ----------
        target_id : Any
            The target id to remove (this is supplied by the record_id callback)
        """

        for row in range(self._completer_model.rowCount()):
            data = self._completer_model.item(row).data(Qt.UserRole)
            record_id = self._record_id_fn(data)
            if record_id == target_id:
                self._completer_model.removeRow(row)
                break

    def _remove_pill(self, pill: PillBadge):
        """Remove a pill

        Parameters
        ----------
        pill : PillBadge
            The pill to remove
        """

        if self.main_layout.indexOf(pill) == -1:
            # The pill was already removed ignore the call
            return

        self.main_layout.removeWidget(pill)
        pill.deleteLater()
        self.main_layout.invalidate()

        # Return the pill data to the dropdown and fix the text field
        self._restore_record(pill.pill_data)
        self._set_placeholder()

    def _setup_selection_box(self):
        """Setup the dropdown menu"""

        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.text_field.setCompleter(self.completer)
        # We create a signal connection with an overload so we can
        # easily (and reliably) get the correct proxy index
        self.completer.activated[QModelIndex].connect(self._on_selected)

    @staticmethod
    def _as_accessor(key_or_fn: str | Callable) -> Any:
        """The function used to access the model. Since we don't know what our model's format is
        it can be either a function, or a str if the model is a dict

        Parameters
        ----------
        key_or_fn : str | Callable
            Either a function of a dict key to grab some information out of the model

        Raises
        ------
        TypeError
            if the provided key_or_fn is not a str or a callable

        Returns
        -------
        Any
            The result of the callback (usually str or int)
        """

        if callable(key_or_fn):
            return key_or_fn
        if isinstance(key_or_fn, str):
            return lambda item: item[key_or_fn]

        raise TypeError(
            f"Accessor must be a str or callable, got {type(key_or_fn).__name__}"
        )
