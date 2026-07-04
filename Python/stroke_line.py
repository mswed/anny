from typing import Optional
import math
from PySide6 import QtGui
from PySide6.QtCore import Qt
from OpenGL import GL

from annotations import Stroke
from utils import (
    ImagePoint,
    ScreenPoint,
    Source,
    LineVerts,
    TickVerts,
    ArrowVerts,
    Color,
)


class LineStroke(Stroke):
    editable_properties = [
        "width",
        "color",
        "opacity",
        "fill_color",
        "fill_opacity",
        "start_cap",
        "end_cap",
        "text",
        "font",
    ]

    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: Source,
        width: float = 1.0,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1.0,
        fill_color: tuple = (1, 1, 1, 1),
        fill_opacity: float = 1.0,
        start_cap: str = "",
        end_cap: str = "",
        text: str = "",
        font: QtGui.QFont = QtGui.QFont("Arial", 14),
        **kwargs,
    ) -> None:
        """Create a line stroke. The line can start or end with an arrow, a circle or a tick

        Parameters
        ----------
        start : ImagePoint
            The first point in the stroke
        end : ImagePoint
            The last point in the stroke
        source : Source
            The source the stroke is attached to
        width : float
            The outline width
        color : tuple
            The outline color
        opacity : float
            The outline opacity
        fill_color : tuple
            The fill color
        fill_opacity : float
            The fill opacity
        start_cap : str
            The type of the start cap can be empty, arrow, circle or tick
        end_cap : str
            The type of the end cap can be empty, arrow, circle or tick
        text : str
            Optinal text to show on at the center of the line
        font : QtGui.QFont
            The font to draw the text in
        **kwargs
            Any additional kwargs the caller might pass (at the moment all are ignored)

        """
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )
        self.start_cap = start_cap
        self.end_cap = end_cap
        self.text = text
        self.font = font

    def __repr__(self) -> str:
        return f"<LineStroke> start={self.start} end={self.end} color={self.color}"

    def detect_selection(self, position: ImagePoint) -> bool:
        """Detect if the stroke was selected

        Parameters
        ----------
        position : ImagePoint
            The position of the mouse click

        Returns
        -------
        bool
            True if selected, False otherwise
        """
        return self._detect_line_selection(position)

    def _detect_line_selection(self, point: ImagePoint) -> bool:
        """The actual selection detection logic. Checks if the clicked point
        is close enough to the line

        Parameters
        ----------
        position : ImagePoint
            The position the user clicked

        Returns
        -------
        bool
            True if the position is close enough to the line else False

        """
        # Find closest stoke to threshold
        THRESHOLD = 0.01

        dist = self._point_to_stroke_distance(self.start, self.end, point)
        return dist < THRESHOLD

    def _get_line_verts(self) -> Optional[LineVerts]:
        """Get the verts needed to draw the line, including caps shape

        Returns
        -------
        Optional[LineVerts]
            The line verts if it can be drawn else None

        """
        # Figure out start and end points in screen space
        # We need to record the original start and end for the handles
        start_anchor = self.start.to_screenspace()
        end_anchor = self.end.to_screenspace()
        if not (start_anchor and end_anchor):
            return

        line_start = start_anchor
        line_end = end_anchor

        # If we have arrows the start and end shrink to the base
        # so that the arrow has a point
        start_arrow = None
        end_arrow = None
        if self.start_cap == "arrow":
            start_arrow = self._get_arrow_verts(start_anchor, end_anchor, "start")
            if start_arrow:
                line_start = start_arrow.line_base
        if self.end_cap == "arrow":
            end_arrow = self._get_arrow_verts(start_anchor, end_anchor, "end")
            if end_arrow:
                line_end = end_arrow.line_base

        # We need all the other information so we can later draw the caps correctly
        direction = start_anchor.direction_to(end_anchor)
        normalized = direction.normalized
        if normalized is None:
            return

        perp = normalized.perpendicular
        offset = perp * self.width
        half_offset = perp * (self.width / 2)

        top_left = line_start
        bottom_left = top_left + offset
        top_right = line_end
        bottom_right = top_right + offset
        mid_left = top_left + half_offset
        mid_right = top_right + half_offset
        midpoint = ScreenPoint(
            (mid_left.x + mid_right.x) / 2, (mid_left.y + mid_right.y) / 2
        )

        return LineVerts(
            bottom_left,
            bottom_right,
            top_right,
            top_left,
            mid_left,
            mid_right,
            start_anchor,
            end_anchor,
            midpoint,
            start_arrow,
            end_arrow,
            perp,
            half_offset,
        )

    def _get_tick_verts(self, line: LineVerts, position: str = "start") -> TickVerts:
        """Get the verts needed to draw a tick cap

        Parameters
        ----------
        position : str
            Where shold we draw the tick? Start or end
        line : LineVerts
            The line's verts including all the data needed to position the tick

        Returns
        -------
        TickVerts
            The verts needed to draw the tick

        """
        # Create a direction vecto
        tick_width = max(self.width * 2, 1)

        # Calculate points
        base = line.mid_left if position == "start" else line.mid_right
        # base + (perp * width)
        top = base + (line.perp * tick_width)
        # base - (perp * width)
        bottom = base - (line.perp * tick_width)

        return TickVerts(top, bottom)

    def _get_arrow_verts(
        self, start_anchor: ScreenPoint, end_anchor: ScreenPoint, position: str = "end"
    ) -> Optional[ArrowVerts]:
        """Get the verts needed to draw an arrow cap

        Parameters
        ----------
        start_anchor : ScreenPoint
            The line's original start point
        end_anchor : ScreenPoint
            The line's original end point
        position : str
            Where should we draw the arrow? Start or end.

        Returns
        -------
        ArrowVerts
            The verts needed to draw the arrow if we can get them (includes the new start or end of the line - line_base), else None

        """
        # Create a direction vector
        if position == "end":
            # Start to end
            direction = start_anchor.direction_to(end_anchor)
        else:
            # End to start
            direction = end_anchor.direction_to(start_anchor)

        # Normalize the vector so we have a unit vector
        normalized = direction.normalized
        if normalized is None:
            # We don't have a vector, we can't draw
            return

        arrow_length = max(self.width * 2, 1)
        arrow_width = arrow_length
        perp = normalized.perpendicular

        # Calculate points
        tip = (
            end_anchor + (perp * (self.width / 2))
            if position == "end"
            else start_anchor - (perp * (self.width / 2))
        )
        base = tip - (normalized * arrow_length * 2)
        left_wing = base + (perp * arrow_width)
        right_wing = base - (perp * arrow_width)

        line_tip = end_anchor if position == "end" else start_anchor
        line_base = line_tip - (normalized * arrow_length * 2)

        return ArrowVerts(tip, left_wing, right_wing, base, line_base)

    def _generate_text_texture(self) -> Optional[QtGui.QImage]:
        """Generate a text texture so we can render it using OpenGL

        Returns
        -------
        Optional[QtGui.QImage]
            The texture image if we have text else None


        """
        if self.text is None:
            return

        # Measure the font so we know how big our texture needs to be
        metrics = QtGui.QFontMetrics(self.font)
        text_rect = metrics.boundingRect(self.text)

        # Padding
        width = text_rect.width() + 8
        height = text_rect.height() + 8

        # Create the image
        image = QtGui.QImage(width, height, QtGui.QImage.Format_RGBA8888)
        image.fill(
            QtGui.QColor.fromRgbF(
                self.fill_color.r,
                self.fill_color.g,
                self.fill_color.b,
                self.fill_color.a,
            )
        )

        # Paint
        painter = QtGui.QPainter(image)
        painter.setFont(self.font)
        painter.setPen(
            QtGui.QColor.fromRgbF(
                self.color.r, self.color.g, self.color.b, self.opacity
            )
        )
        painter.drawText(image.rect(), Qt.AlignCenter, self.text)
        painter.end()

        return image

    def _load_texture(self, image: QtGui.QImage) -> tuple:
        """Load an image into a GL texture. Used to create texts

        Parameters
        ----------
        image : QtGui.QImage
            Image with text

        Returns
        -------
        Tuple
            texture id, width and height

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

        return texture_id, width, height

    def _draw_line(self, verts: LineVerts, color: Color):
        """Draw the line based on the provided verts

        Parameters
        ----------
        verts : LineVerts
            The line verts
        color : Color
            The line's color

        """
        # Square
        GL.glColor4f(color.r, color.g, color.b, color.a)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(*verts.bottom_left)
        GL.glVertex2f(*verts.bottom_right)
        GL.glVertex2f(*verts.top_right)
        GL.glVertex2f(*verts.top_left)
        GL.glEnd()

        # Draw a line around the line to smooth it
        GL.glLineWidth(1)
        GL.glColor4f(self.color[0], self.color[1], self.color[2], self.opacity)
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(*verts.bottom_left)
        GL.glVertex2f(*verts.bottom_right)
        GL.glVertex2f(*verts.top_right)
        GL.glVertex2f(*verts.top_left)
        GL.glEnd()

    def _draw_cap(
        self, cap_type: Optional[str], position: str, line: LineVerts
    ) -> None:
        """Draw the a specicifc cap type at the start or end of the line

        Parameters
        ----------
        cap_type : Optional[str]
            Can be arrow, circle, tick or None
        position : str
            Where should we draw the cap? Start or end
        line : LineVerts
            The line's verts so we can place the cap
        """
        if cap_type is None:
            return

        if cap_type == "arrow":
            self._draw_arrow(line.start_anchor, line.end_anchor, position)
        elif cap_type == "tick":
            self._draw_tick(line, position)
        elif cap_type == "circle":
            self._draw_circle(line, position)
        else:
            print("Unknown cap type", cap_type)

    def _draw_tick(self, line: LineVerts, position: str = "start"):
        """Draw a tick cap based on the provided verts

        Parameters
        ----------
        line : LineVerts
            The line verts so we can calcualte the tick
        position : str
            Where whould we draw the tick? Start or end.

        """
        verts = self._get_tick_verts(line, position)
        if verts:
            GL.glLineWidth(self.width / 2)
            GL.glColor4f(self.color[0], self.color[1], self.color[2], self.opacity)
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(*verts.top)
            GL.glVertex2f(*verts.bottom)
            GL.glEnd()

    def _draw_arrow(
        self, start_anchor: ScreenPoint, end_anchor: ScreenPoint, position: str = "end"
    ):
        """Draw the arrow cap based on the start and end points

        Parameters
        ----------
        start_anchor : ScreenPoint
            The line's original start point
        end_anchor : ScreenPoint
            The line''s original end point
        position : str
            Where should we draw the arrow? Start or end.

        """
        verts = self._get_arrow_verts(start_anchor, end_anchor, position)
        if verts:
            # We only draw if we got verts
            # Draw
            GL.glColor4f(self.color[0], self.color[1], self.color[2], self.opacity)
            GL.glBegin(GL.GL_TRIANGLES)
            GL.glVertex2f(*verts.tip)
            GL.glVertex2f(*verts.left_wing)
            GL.glVertex2f(*verts.right_wing)
            GL.glEnd()

            # Draw a line around the arrow head to smooth it
            GL.glLineWidth(1)
            GL.glColor4f(self.color[0], self.color[1], self.color[2], self.opacity)
            GL.glBegin(GL.GL_LINE_LOOP)
            GL.glVertex2f(*verts.tip)
            GL.glVertex2f(*verts.left_wing)
            GL.glVertex2f(*verts.right_wing)
            GL.glEnd()

    def _draw_circle(self, line: LineVerts, position: str) -> None:
        """
        Draw a GL circle at the start or end of the line

        Parameters
        ----------
        line : LineVerts
            The drawn line points
        position : str
            Where should we draw the circle? start or end?

        """
        segments = 16
        radius = max(self.width * 1.5, 4)
        center = line.mid_left if position == "start" else line.mid_right

        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2f(*center)
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            GL.glVertex2f(
                center.x + math.cos(angle) * radius, center.y + math.sin(angle) * radius
            )
        GL.glEnd()

    def _draw_text(
        self, midpoint: ScreenPoint, width: float, height: float, texture_id: int
    ):
        """Draw text in the middle of the line

        Parameters
        ----------
        midpoint : ScreenPoint
            The middle of the line
        width : float
            The width of the text texture
        height : float
            The height of the text texture
        texture_id : int
            The texture id to load

        """
        # Enable and bind
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)

        half_w = width / 2
        half_h = height / 2

        # Calculate rotation
        direction = self.start.direction_to(self.end)
        angle = math.atan2(direction.y, direction.x)

        # Clamp the angle so the text is always readable
        if angle > math.pi / 2:
            angle -= math.pi
        elif angle < -math.pi / 2:
            angle += math.pi

        # Temporeratly move the drawing to relative mode around 0, 0 so we can rotate
        GL.glPushMatrix()
        GL.glTranslatef(midpoint.x, midpoint.y, 0)
        GL.glRotatef(math.degrees(angle), 0, 0, 1)

        GL.glBegin(GL.GL_QUADS)
        GL.glColor4f(1.0, 1.0, 1.0, self.opacity)
        # Map texture points to relative points
        GL.glTexCoord2f(0, 1)  # Bottom left
        GL.glVertex2f(-half_w, -half_h)
        GL.glTexCoord2f(1, 1)  # Bottom right
        GL.glVertex2f(half_w, -half_h)
        GL.glTexCoord2f(1, 0)  # Top right
        GL.glVertex2f(half_w, half_h)
        GL.glTexCoord2f(0, 0)  # Top left
        GL.glVertex2f(-half_w, half_h)
        GL.glEnd()

        # Cleanup
        GL.glPopMatrix()
        GL.glDisable(GL.GL_TEXTURE_2D)

    def render(self):
        # Antialiasing
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

        verts = self._get_line_verts()
        if not verts:
            return

        self._draw_line(verts, self.color)

        # Draw the caps
        self._draw_cap(self.start_cap, "start", verts)
        self._draw_cap(self.end_cap, "end", verts)

        # Draw the text
        if self.text:
            qt_texture = self._generate_text_texture()
            if qt_texture:
                tid, tw, th = self._load_texture(qt_texture)
                self._draw_text(verts.midpoint, tw, th, tid)

        # Selection highlighting
        if self.selected:
            edges = self._get_bounding_box_edges()
            if edges:
                self._draw_bounding_box(edges)
            self._draw_handle(verts.start_anchor + verts.half_offset)
            self._draw_handle(verts.end_anchor + verts.half_offset)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)
