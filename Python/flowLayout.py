from PySide6.QtCore import QRect, Qt, QSize
from PySide6.QtWidgets import (
    QApplication,
    QLayout,
    QSizePolicy,
    QWidget,
    QLayoutItem,
    QWidgetItem,
)


class FlowLayout(QLayout):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(0, 0, 0, 0)

        self._items_list: list[QLayoutItem] = []
        self._stretch_widget = None

    @property
    def stretch_widget(self):
        return self._stretch_widget

    @stretch_widget.setter
    def stretch_widget(self, item):
        self._stretch_widget = item

    def __del__(self):
        """When the layout is deleted we remove all of its items"""

        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item: QLayoutItem) -> None:
        """When we add an item to the layout we simply add it to the items list

        Parameters
        ----------
        item : QLayoutItem
            Item to add
        """
        self._items_list.append(item)

    def insertWidget(self, index: int, widget: QWidget) -> None:
        # The widget needs to be a child of the layout
        self.addChildWidget(widget)

        # We need to wrap the widget in a QWidgetItem (since that's what our list of items expects)
        item = QWidgetItem(widget)
        self._items_list.insert(index, item)

        # Invalidate the layout so it redraws
        self.invalidate()

    def count(self) -> int:
        """How many items does the layout contain?

        Returns
        -------
        int
            Number of items in the layout
        """
        return len(self._items_list)

    def itemAt(self, index: int) -> QLayoutItem | None:
        """Peak at an item in the items list

        Parameters
        ----------
        index : int
            Index to peak at

        Returns
        -------
        QLayoutItem | None
            Item if the index is valid else None

        """
        if 0 <= index < len(self._items_list):
            return self._items_list[index]

        return None

    def takeAt(self, index: int) -> QLayoutItem | None:
        """Pop an item in the items list and return it

        Parameters
        ----------
        index : int
            Index to grab and remove

        Returns
        -------
        QLayoutItem | None
            Item if the index is valid else None

        """
        if 0 <= index < len(self._items_list):
            return self._items_list.pop(index)

        return None

    def expandingDirections(self) -> Qt.Orientation:
        """Our layout only expands horizontaly

        Returns
        -------
        Qt.Orientation
            Horizontal oriantation

        """
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        """Our layout's prefered height depends on its width

        Returns
        -------
        bool
            Always true

        """
        return True

    def heightForWidth(self, width: int) -> int:
        """Calculate the layout's prefered height based on its width

        Parameters
        ----------
        width : int
            The layout's width

        Returns
        -------
        int
            The layout's prefered height

        """
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect: QRect) -> None:
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        """Calculate the layout's minimum size based on its wigets

        Returns
        -------
        QSize
            The minumal size of the layout

        """
        size = QSize()

        for item in self._items_list:
            # Expand the items to their minimum size
            size = size.expandedTo(item.minimumSize())

        # Add margins (in an asymetric way unlike the original Qt referene code)
        margins = self.contentsMargins()
        size += QSize(
            (margins.left() + margins.right()), (margins.top() + margins.bottom())
        )

        return size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        """Calculate the position of the layouts items and optionally place them

        Parameters
        ----------
        rect : QRect
            The rect containing the items
        test_only : bool
            True if we only want to get the height of the layout, False if we want to
            build the layout

        Returns
        -------
        int
            The height of the layout

        """
        x = rect.x()
        y = rect.y()

        line_height = 0

        spacing = self.spacing()

        # We grab the style from the app instead of the widget so it doesn't
        # get garbage collected by RV
        style = QApplication.style()

        # For each widget calculate the space between it and the next one
        layout_spacing_x = style.layoutSpacing(
            QSizePolicy.ControlType.PushButton,
            QSizePolicy.ControlType.PushButton,
            Qt.Orientation.Horizontal,
        )
        layout_spacing_y = style.layoutSpacing(
            QSizePolicy.ControlType.PushButton,
            QSizePolicy.ControlType.PushButton,
            Qt.Orientation.Vertical,
        )

        space_x = spacing + layout_spacing_x
        space_y = spacing + layout_spacing_y

        for item in self._items_list:
            hint = item.sizeHint()
            # We first grab the widget's actual width
            natural_width = hint.width()

            # Calculate the x of the next widget
            next_x = x + natural_width + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                # We have reached our width limit, create a new line and
                # recalculate the next x position. But we only do so if we
                # already placed an item on this line (our height isn't 0)
                x = rect.x()
                y = y + line_height + space_y
                # We also reset the height of this new row
                line_height = 0

            # We now calculate the placement width
            placement_width = natural_width
            if item.widget() is self.stretch_widget:
                placement_width = max(natural_width, rect.right() - x)

            if not test_only:
                # We are not just checking the size of the layout
                # We are reformatting it. Place the widget
                item.setGeometry(QRect(x, y, placement_width, hint.height()))

            # Update our x position so the loop can continue
            x = x + placement_width + space_x
            line_height = max(line_height, hint.height())

        # Return the overall height of the layout
        return y + line_height - rect.y()
