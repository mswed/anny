from PySide6.QtGui import QIcon, QEnterEvent, QPainter, QPixmap, QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize, QEvent, Signal


class PillBadge(QFrame):
    """A pill widget for multiselects. Has an icon, pill text, pill data, and a remove button"""

    deleteRequested = Signal(object)

    def __init__(self, text, icon, data=None, color="#e0922f", parent=None) -> None:
        super().__init__(parent)
        self.pill_text = text
        self.pill_icon = icon
        self.pill_data = data
        self.color = color

        layout = QHBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 3, 8, 3)

        self.setObjectName("PillBadge")
        self.setFixedHeight(24)
        self.setStyleSheet(
            f"""
            #PillBadge {{
                background-color: {self.color};
                border-radius: 12px;
            }}
            """
        )

        # Set the icon
        left = QLabel()
        if self.pill_icon:
            icon = QIcon(self.pill_icon)
            icon_size = QSize(16, 16)
            pixmap = icon.pixmap(icon_size)
            left.setStyleSheet("background: transparent;")
            tinted_icon = self._tint(pixmap, "white")
            left.setPixmap(tinted_icon)

        # Set the text
        middle = QLabel(self.pill_text)
        middle.setStyleSheet("color: white; background: transparent;")

        # Set the close button
        icon_path = ":/icons/xmark-solid-full.svg"
        self.close_icon = self._build_icon(icon_path)
        self.delete_btn = QPushButton()
        self.delete_btn.setFixedSize(16, 16)
        self.delete_btn.setObjectName("PillCloseBtn")
        self.delete_btn.setStyleSheet(
            f"""
            QPushButton {{background: transparent; border: none;}}
            QPushButton:enabled {{color: white; }}
            QPushButton:disabled {{color:  {self.color}; }}
            """
        )
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self._on_delete_clicked)

        # Add all to layout
        layout.addWidget(left)
        layout.addWidget(middle)
        layout.addWidget(self.delete_btn)

    def enterEvent(self, event: QEnterEvent) -> None:
        """Enable and display the remove button when we hover over the pill

        Parameters
        ----------
        event : QEnterEvent
            The Qt enter event

        """
        self.delete_btn.setEnabled(True)
        self.delete_btn.setIcon(self.close_icon)

    def leaveEvent(self, event: QEvent) -> None:
        """Disable and hide the remove button when we are no longer over the pill

        Parameters
        ----------
        event : QEvent
            The Qt leave event

        """
        self.delete_btn.setEnabled(False)
        self.delete_btn.setIcon(QIcon())

    def _on_delete_clicked(self):
        """Mark the pill for deletion when we click the remove button"""
        self.deleteRequested.emit(self)

    def _build_icon(self, path: str) -> QIcon:
        """Build the icon and color it

        Parameters
        ----------
        path : str
            The path to the icon

        Returns
        -------
        QIcon
            The icon with the coor applied to it

        """
        icon = QIcon(path)
        icon_size = QSize(16, 16)
        pixmap = icon.pixmap(icon_size)
        tinted_icon = self._tint(pixmap, "white")

        final_icon = QIcon(tinted_icon)

        return final_icon

    @staticmethod
    def _tint(pixmap: QPixmap, color: str) -> QPixmap:
        """Color an icon

        Parameters
        ----------
        pixmap : QPixmap
            The icon pixmap
        color : str
            The color of the tint

        Returns
        -------
        QPixmap
            Tinted pixmap

        """
        # Create a transparent image the size of the icon
        canvas = QPixmap(pixmap.size())
        canvas.fill(Qt.transparent)

        # Create a painter and draw the icon
        p = QPainter(canvas)
        # draw the original icon
        p.drawPixmap(0, 0, pixmap)  # Keep the alpha and replace the color
        p.setCompositionMode(QPainter.CompositionMode_SourceIn)
        p.fillRect(canvas.rect(), QColor(color))
        p.end()

        return canvas
