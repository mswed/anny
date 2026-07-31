from typing import Callable, Optional
from PySide6.QtCore import QModelIndex, QTimer, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QCompleter, QLineEdit, QSizePolicy, QWidget
from flowLayout import FlowLayout
from pill_badge import PillBadge


class MultiSelect(QWidget):
    def __init__(
        self,
        model: list,
        record_name: str | Callable,
        record_id: str | Callable,
        record_type: str | Callable,
        icons: Optional[dict] = None,
        placeholder="Search people and groups",
        parent=None,
    ):
        super().__init__(parent)
        self._record_name_fn = self._as_accessor(record_name)
        self._record_id_fn = self._as_accessor(record_id)
        self._record_type_fn = self._as_accessor(record_type)
        self._icons = icons
        self._placeholder = placeholder
        self._model = model

        self._completer_model = QStandardItemModel(self)
        for record in self._model:
            item = self._create_record(record)
            self._completer_model.appendRow(item)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.main_layout = FlowLayout(self)
        self.text_field = QLineEdit()
        self.completer = QCompleter(self._completer_model, self)
        self._setup_selection_box()

        self.main_layout.addWidget(self.text_field)
        self.main_layout.stretch_widget = self.text_field

    def selected_data(self):
        result = []
        for i in range(self.main_layout.count()):
            w = self.main_layout.itemAt(i).widget()
            if isinstance(w, PillBadge):
                result.append(w.pill_data)

        print(result)
        return result

    def _create_record(self, data: dict) -> QStandardItem:
        display = self._record_name_fn(data)
        item = QStandardItem(display)
        item.setData(data, Qt.UserRole)
        return item

    def _restore_record(self, data: dict):
        item = self._create_record(data)
        self._completer_model.appendRow(item)

    def _on_selected(self, index):
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
        self._remove_record(record_id)

        # Use a timer to clear the field once we're done
        QTimer.singleShot(0, self.text_field.clear)

    def _create_pill(self, text, data):
        record_type = self._record_type_fn(data)

        icon = None
        if self._icons is not None:
            icon = self._icons.get(record_type)

        pill = PillBadge(text, icon, data=data)
        pill.deleteRequested.connect(self._remove_pill)
        return pill

    def _remove_record(self, target_id):
        for row in range(self._completer_model.rowCount()):
            data = self._completer_model.item(row).data(Qt.UserRole)
            record_id = self._record_id_fn(data)
            if record_id == target_id:
                self._completer_model.removeRow(row)
                break

    def _remove_pill(self, pill: PillBadge):
        if self.main_layout.indexOf(pill) == -1:
            # The pill was already removed ignore the call
            return

        self.main_layout.removeWidget(pill)
        pill.deleteLater()
        self.main_layout.invalidate()

        # Return the pill data to the dropdown
        self._restore_record(pill.pill_data)

    def _setup_selection_box(self):
        self.text_field.setPlaceholderText(self._placeholder)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.text_field.setCompleter(self.completer)
        # We create a signal connection with an overload so we can
        # easily (and reliably) get the correct proxy index
        self.completer.activated[QModelIndex].connect(self._on_selected)

    @staticmethod
    def _as_accessor(key_or_fn):
        if callable(key_or_fn):
            return key_or_fn
        if isinstance(key_or_fn, str):
            return lambda item: item[key_or_fn]

        raise TypeError(
            f"Accessor must be a str or callable, got {type(key_or_fn).__name__}"
        )
