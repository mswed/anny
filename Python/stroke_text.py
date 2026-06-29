from PySide6 import QtGui
from PySide6.QtCore import Qt
from typing import Optional
from OpenGL import GL

from annotations import Stroke
from utils import ImagePoint, ScreenPoint, SourceName, RectEdges, Color


class TextStroke(Stroke):
    editable_properties = [
        "width",
        "color",
        "opacity",
        "fill_color",
        "fill_opacity",
        "text",
        "font",
    ]

    MARGIN = 8

    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: SourceName,
        width: float = 1,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1,
        fill_color: tuple = (1, 1, 1, 1),
        fill_opacity: float = 1,
        text: Optional[str] = "",
        font: QtGui.QFont = QtGui.QFont("Arial", 14),
        **kwargs,
    ) -> None:
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )
        self.text = text
        self.font = font

    def __repr__(self) -> str:
        return f"<TextStroke> start={self.start} end={self.end} color={self.color}"

    def detect_selection(self, position: ImagePoint) -> bool:
        """Check if a stroke was selected

        Parameters
        ----------
        position : ImagePoint
            The position of the mouse click

        Returns
        -------
        bool
            True if selected, False otherwise

        """
        return self._point_inside_stroke(position)

    def _point_inside_stroke(self, point: ImagePoint) -> bool:
        """Check if a click happened inside a stroke

        Parameters
        ----------
        point : ImagePoint
            Where the user clicked

        Returns
        -------
        bool
            True if stroke was clicked false otherwise
        """

        # Strokes are drawn in screen space, so convert to event space first
        hp = point.to_screenspace()
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        if hp and start and end:
            edges = self._get_rect_edges(start, end)

            return edges.right > hp.x > edges.left and edges.top > hp.y > edges.bottom

        return False

    def _get_rect_edges(self, start: ScreenPoint, end: ScreenPoint) -> RectEdges:
        """Get the edges of the full stroke rectangle, used to draw both fill and text

        Parameters
        ----------
        start : ScreenPoint
            Rect start point
        end : ScreenPoint
            Rect end point

        Returns
        -------
        RectEdges
            The edges of the rectangle

        """
        # Most values come from the original drag
        left = min(start.x, end.x)
        right = max(start.x, end.x)
        top = max(start.y, end.y)

        # But the height is calcualted based on either the drag or the size
        # of the text
        height = self._get_rect_height()
        bottom = top - height

        return RectEdges(left, right, top, bottom)

    def _get_rect_height(self) -> float:
        """
        Get the height of the box containing the text. The minimal height (while editing) is what the user drew.
        Once editing is done the height snaps to match the actual height of the text.

        Returns
        -------
        float
            The height of the box as an int. If there's text this value includes the margins as well
        """

        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        if start and end:
            # The height as set by the user
            dragged_height = abs(end.y - start.y)

            if not self.text:
                return dragged_height

            # The width is set by the user drawing the rect. But we add the margins to it
            # so text wrapping works correctly
            width = max(int(abs(end.x - start.x) - 2 * self.MARGIN), 1)

            # We have text measure it to determine height
            metrics = QtGui.QFontMetrics(self.font)
            flags = Qt.TextWordWrap | Qt.AlignLeft
            # We calculate the inset width for correct text wrapping
            rect = metrics.boundingRect(0, 0, int(width), 10000, flags, self.text)
            # We add the margins to the height
            text_height = rect.height() + 2 * self.MARGIN

            if self.editing:
                # As long as we're editing the height can only extend, never shrink
                return max(dragged_height, text_height)

            else:
                # we are done editing use the text height even if it means shrinking
                return text_height

        return 0.0

    def _generate_text_texture(self) -> Optional[QtGui.QImage]:
        """Generate a text texture so we can render it using OpenGL

        Returns
        -------
        Optional[QtGui.QImage]
            The texture image
        """
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()
        if not self.text or not start or not end:
            return

        # Margins
        width = abs(end.x - start.x)
        width = max(int(width - 2 * self.MARGIN), 1)
        # get rect height gives us the height of the rect WITH margins
        # so we remove them to get the proper padding
        height = max(self._get_rect_height() - 2 * self.MARGIN, 1)

        # Create the image
        image = QtGui.QImage(width, height, QtGui.QImage.Format_RGBA8888)
        # The actual fill comes from the drawn rect
        image.fill(Qt.transparent)

        # Paint
        painter = QtGui.QPainter(image)
        painter.setFont(self.font)
        r, g, b, a = self.color
        painter.setPen(QtGui.QColor.fromRgbF(r, g, b, a))

        flags = Qt.TextWordWrap | Qt.AlignLeft

        painter.drawText(image.rect(), flags, self.text)
        painter.end()

        return image

    def _load_texture(self, image: QtGui.QImage) -> int:
        """Load an image into a GL texture. Used to create texts

        Parameters
        ----------
        image : QtGui.QImage
            Image with text

        Returns
        -------
        int
            texture id

        """

        width = image.width()
        height = image.height()

        # Image in bytes
        pointer = image.constBits()

        texture_id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(
            GL.GL_TEXTURE_2D,
            0,
            GL.GL_RGBA,
            width,
            height,
            0,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
            pointer,
        )

        return texture_id

    def _draw_rect(self, edges: RectEdges, color: Color):
        """Draw the main rectangle (the fill)

        Parameters
        ----------
        edges : RectEdges
            Rectangle edges
        color : Color
            Rectangle color

        """
        # Square
        GL.glColor4f(color.r, color.g, color.b, color.a)
        GL.glBegin(GL.GL_QUADS)
        for corner in edges.corners:
            GL.glVertex2f(*corner)
        GL.glEnd()

    def _draw_text(self, edges: RectEdges, texture_id: int) -> None:
        """Draw the text texture

        Parameters
        ----------
        edges : RectEdges
            The text edges
        texture_id : int
            The texture id

        """
        # Enable and bind
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)

        GL.glBegin(GL.GL_QUADS)
        GL.glColor4f(1.0, 1.0, 1.0, self.opacity)
        # Map texture points to relative points
        GL.glTexCoord2f(0, 1)  # Bottom left
        GL.glVertex2f(*edges.bottom_left)
        GL.glTexCoord2f(1, 1)  # Bottom right
        GL.glVertex2f(*edges.bottom_right)
        GL.glTexCoord2f(1, 0)  # Top right
        GL.glVertex2f(*edges.top_right)
        GL.glTexCoord2f(0, 0)  # Top left
        GL.glVertex2f(*edges.top_left)
        GL.glEnd()

        # Cleanup
        GL.glDisable(GL.GL_TEXTURE_2D)

    def render(self):

        # Antialiasing
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        if start and end:
            e = self._get_rect_edges(start, end)

            # Square
            r, g, b, a = self.fill_color
            GL.glColor4f(r, g, b, a)
            GL.glBegin(GL.GL_QUADS)
            for corner in e.corners:
                GL.glVertex2f(corner.x, corner.y)
            GL.glEnd()

            # # Draw the text
            if self.text:
                qt_texture = self._generate_text_texture()
                if qt_texture:
                    tid = self._load_texture(qt_texture)
                    self._draw_text(e.inset(self.MARGIN), tid)

            # Selection highlighting
            if self.selected:
                self._draw_bounding_box(e)
                self._draw_handle(start)
                self._draw_handle(end)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)
