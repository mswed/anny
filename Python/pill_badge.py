from PySide6.QtGui import QIcon, QEnterEvent, QPainter, QPixmap, QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QSize, QEvent, Signal


class PillBadge(QFrame):
    deleteRequested = Signal(object)

    def __init__(self, text, icon, data=None, color="#e0922f", parent=None) -> None:
        super().__init__(parent)
        self.pill_text = text
        self.pill_icon = icon
        self.pill_data = data
        self.color = color

        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 5, 15, 5)

        self.setObjectName("PillBadge")
        self.setStyleSheet(
            f"""
            #PillBadge {{
                background-color: {self.color};
                border-radius: 15px
            }}
            """
        )

        # Set the icon
        if self.pill_icon:
            icon = QIcon(self.pill_icon)
            icon_size = QSize(16, 16)
            pixmap = icon.pixmap(icon_size)
            left = QLabel()
            left.setStyleSheet("background: transparent;")
            tinted_icon = self._tint(pixmap, "white")
            left.setPixmap(tinted_icon)

        # Set the text
        middle = QLabel(self.pill_text)
        middle.setStyleSheet("color: white; background: transparent;")

        # Set the close button
        self.delete_btn = QPushButton("X")
        self.delete_btn.setMaximumWidth(15)
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
        self.delete_btn.setEnabled(True)

    def leaveEvent(self, event: QEvent, /) -> None:
        self.delete_btn.setEnabled(False)

    def _on_delete_clicked(self):
        self.deleteRequested.emit(self)

    @staticmethod
    def _tint(pixmap: QPixmap, color: str) -> QPixmap:
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
