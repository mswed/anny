from collections import defaultdict
import math
from typing import Optional, Tuple, NamedTuple
from OpenGL import GL
from PySide6 import QtGui
from PySide6.QtCore import Qt
import rv.commands as crv
from utils import ImagePoint, ScreenPoint


class SquareVerts(NamedTuple):
    bottom_left: ScreenPoint
    bottom_right: ScreenPoint
    top_right: ScreenPoint
    top_left: ScreenPoint


class ArrowVerts(NamedTuple):
    tip: ScreenPoint
    left_wing: ScreenPoint
    right_wing: ScreenPoint
    base: ScreenPoint


class TickVerts(NamedTuple):
    top: ScreenPoint
    bottom: ScreenPoint


class AnnotationLayer:
    """
    The base class that renders the actual annotations. Annotations are added to the strokes dict and then
    rendered via the stroke's render function
    """

    def __init__(self) -> None:
        self.strokes = defaultdict(list)

    def render(self, event):

        # Get viewport size
        w, h = event.domain()

        # Get frame
        frame = crv.frame()

        # Setup projection
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, w, 0, h, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        frame_strokes = self.strokes.get(frame)
        if frame_strokes:
            for stroke in frame_strokes:
                stroke.render()


class Stroke:
    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
        width: float = 1.0,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1.0,
    ) -> None:
        self.start = start
        self.end = end
        self.source = source
        self.width = width
        self.color = color
        self.opacity = opacity
        self.selected = False

    def get_handle_verts(self, point: ScreenPoint) -> SquareVerts:
        size = 6
        half = size / 2

        bottom_left = ScreenPoint((point.x - half, point.y - half))
        bottom_right = ScreenPoint((point.x + half, point.y - half))
        top_right = ScreenPoint((point.x + half, point.y + half))
        top_left = ScreenPoint((point.x - half, point.y + half))

        return SquareVerts(bottom_left, bottom_right, top_right, top_left)

    def move(self, dx: float, dy: float, move_type: str = "stroke"):
        """Move the annotation or one of its points. All movement is calcualted in image space

        Parameters
        ----------
        move_type : str
            What are we moving? stroke, start or end?
        dx : float
            Delta between original point and new point
        dy : float
            Delta between original point and new point
        """

        if move_type == "stroke" or move_type == "start":
            self.start.move(dx, dy)
        if move_type == "stroke" or move_type == "end":
            self.end.move(dx, dy)

    def point_inside_handle(self, point: ImagePoint, position: str) -> bool:
        """Check if a click happened inside a handle

        Parameters
        ----------
        point : ImagePoint
            Where the user clicked
        position : str
            Which handle are we checking against? Start or end?

        Returns
        -------
        bool
            True if handle was clicked false otherwise
        """

        # Handles are drawn in screen space, so convert to event space first
        hp = point.to_screenspace()

        if position == "start":
            handle_verts = self.get_handle_verts(self.start.to_screenspace())
        else:
            handle_verts = self.get_handle_verts(self.end.to_screenspace())

        x_start = handle_verts.bottom_left.x
        x_end = handle_verts.bottom_right.x
        y_start = handle_verts.top_left.y
        y_end = handle_verts.bottom_left.y

        return x_end > hp.x > x_start and y_start > hp.y > y_end

    def point_to_stroke_distance(self, point):
        """
        Calculate the distance from the mouse click to the stroke. Used for selection.
        """

        # Get the points coordinates
        px, py = point
        x1, y1 = self.start
        x2, y2 = self.end

        # Calculate distances
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            # Our stroke has no length, it's a dot
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)

        # Find the point on the stroke that is closest to our click
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        # Clamp it so it only applies to the actual stroke
        t = max(0, min(1, t))

        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy

        return math.sqrt((px - nearest_x) ** 2 + (py - nearest_y) ** 2)

    def draw_bounding_box(self):
        """
        Draw a box around the annotation to mark a selection
        """

        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        # get min and max with padding
        padding = 6
        min_x = min(start.x, end.x) - padding
        max_x = max(start.x, end.x) + padding
        min_y = min(start.y, end.y) - padding
        max_y = max(start.y, end.y) + padding

        GL.glEnable(GL.GL_LINE_STIPPLE)
        GL.glLineStipple(1, 0xF0F0)
        GL.glLineWidth(1.0)
        GL.glColor4f(1.0, 1.0, 1.0, 0.8)

        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(min_x, min_y)
        GL.glVertex2f(max_x, min_y)
        GL.glVertex2f(max_x, max_y)
        GL.glVertex2f(min_x, max_y)
        GL.glEnd()

        GL.glDisable(GL.GL_LINE_STIPPLE)

    def draw_handle(self, point: ScreenPoint):

        verts = self.get_handle_verts(point)
        # Square
        GL.glColor4f(1.0, 1.0, 1.0, 1.0)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(*verts.bottom_left)
        GL.glVertex2f(*verts.bottom_right)
        GL.glVertex2f(*verts.top_right)
        GL.glVertex2f(*verts.top_left)
        GL.glEnd()

        # Border
        GL.glColor4f(0, 0, 0, 1.0)
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(*verts.bottom_left)
        GL.glVertex2f(*verts.bottom_right)
        GL.glVertex2f(*verts.top_right)
        GL.glVertex2f(*verts.top_left)
        GL.glEnd()

    def render(self):
        pass


class LineStroke(Stroke):
    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
        width: float = 1.0,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1.0,
        start_cap: Optional[str] = None,
        end_cap: Optional[str] = None,
        text: Optional[str] = None,
    ) -> None:
        super().__init__(start, end, source, width, color, opacity)
        self.start_cap = start_cap
        self.end_cap = end_cap
        self.text = text

        self.text = "hello, world"

    def __repr__(self) -> str:
        return f"<LineStroke> start: {self.start} end: {self.end} color: {self.color}"

    def get_tick_verts(self, position="start"):

        # We start by switching to screenspace
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        # Create a direction vector
        direction = start.direction_to(end)

        # Normalize the vector so we have a unit vector
        normalized = direction.normalized
        if normalized is None:
            # We don't have a vector, we can't draw
            return

        tick_width = max(self.width * 2, 1)
        perp = normalized.perpendicular

        # Calculate points
        base = start if position == "start" else end
        # base + (perp * width)
        top = base + (perp * tick_width)
        # base - (perp * width)
        bottom = base - (perp * tick_width)

        return TickVerts(top, bottom)

    def get_arrow_verts(self, position="end"):
        # We start by switching to screenspace
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        # Create a direction vector
        if position == "end":
            # Start to end
            direction = start.direction_to(end)
        else:
            # End to start
            direction = end.direction_to(start)

        # Normalize the vector so we have a unit vector
        normalized = direction.normalized
        if normalized is None:
            # We don't have a vector, we can't draw
            return

        arrow_length = max(self.width * 2, 1)
        arrow_width = arrow_length
        perp = normalized.perpendicular

        # Calculate points
        tip = end if position == "end" else start
        base = tip - (normalized * arrow_length * 2)
        left_wing = base + (perp * arrow_width)
        right_wing = base - (perp * arrow_width)

        return ArrowVerts(tip, left_wing, right_wing, base)

    def _generate_text_texture(self) -> Optional[QtGui.QImage]:
        """Generate a text texture so we can render it using OpenGL

        Returns
        -------
        Optional[QtGui.QImage]
            The texture image


        """
        if self.text is None:
            return

        font = QtGui.QFont("Ariel", 14)

        # Measure the font so we know how big our texture needs to be
        metrics = QtGui.QFontMetrics(font)
        text_rect = metrics.boundingRect(self.text)

        # Padding
        width = text_rect.width() + 8
        height = text_rect.height() + 8

        # Create the image
        image = QtGui.QImage(width, height, QtGui.QImage.Format_RGBA8888)
        image.fill(Qt.transparent)

        # Paint
        painter = QtGui.QPainter(image)
        painter.setFont(font)
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.drawText(image.rect(), Qt.AlignCenter, self.text)
        painter.end()

        return image

    def _load_texture(self, image: QtGui.QImage) -> Tuple:
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

    def draw_tick(self, position="start"):
        verts = self.get_tick_verts(position)
        if verts:
            GL.glLineWidth(self.width / 2)
            GL.glColor4f(self.color[0], self.color[1], self.color[2], self.opacity)
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(*verts.top)
            GL.glVertex2f(*verts.bottom)
            GL.glEnd()

    def draw_arrow(self, position: str = "end") -> None:
        verts = self.get_arrow_verts(position)
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

    def draw_circle(self, position: str = "start") -> None:
        """
        Draw a GL circle at the start or end of the line

        Parameters
        ----------
        position : str
            Position to draw in: start or end

        """
        segments = 16
        radius = max(self.width * 1.5, 4)
        if position == "start":
            center = self.start.to_screenspace()
        else:
            center = self.end.to_screenspace()

        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2f(*center)
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            GL.glVertex2f(
                center.x + math.cos(angle) * radius, center.y + math.sin(angle) * radius
            )
        GL.glEnd()

    def draw_text(
        self, midpoint: ScreenPoint, width: float, height: float, texture_id: int
    ) -> None:
        # Enable and bind
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)

        # Set color
        GL.glColor4f(1.0, 1.0, 1.0, self.opacity)

        half_w = width / 2
        half_h = height / 2

        GL.glBegin(GL.GL_QUADS)

        # Map texture points to screen points
        GL.glTexCoord2f(0, 1)  # Bottom left
        GL.glVertex2f(midpoint.x - half_w, midpoint.y - half_h)
        GL.glTexCoord2f(1, 1)  # Bottom right
        GL.glVertex2f(midpoint.x + half_w, midpoint.y - half_h)
        GL.glTexCoord2f(1, 0)  # Top right
        GL.glVertex2f(midpoint.x + half_w, midpoint.y + half_h)
        GL.glTexCoord2f(0, 0)  # Top left
        GL.glVertex2f(midpoint.x - half_w, midpoint.y + half_h)
        GL.glEnd()

        # Cleanup
        GL.glDisable(GL.GL_TEXTURE_2D)

    def render(self):
        # Antialiasing
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

        # Figure out start and end points in screen space
        line_start = self.start.to_screenspace()
        line_end = self.end.to_screenspace()
        print("image space points", *self.start, *self.end)
        print("screen space points", *line_start, *line_end)

        # If we have arrows the start and end shrink to the base
        # so the arrow has a point
        if self.start_cap == "arrow":
            verts = self.get_arrow_verts("start")
            if verts:
                line_start = verts.base
        if self.end_cap == "arrow":
            verts = self.get_arrow_verts("end")
            if verts:
                line_end = verts.base

        # Draw the base line
        GL.glLineWidth(self.width)
        GL.glColor4f(self.color[0], self.color[1], self.color[2], self.opacity)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(*line_start)
        GL.glVertex2f(*line_end)
        GL.glEnd()

        # Draw the caps
        if self.end_cap == "arrow":
            self.draw_arrow("end")
        if self.start_cap == "arrow":
            self.draw_arrow("start")
        if self.end_cap == "tick":
            self.draw_tick("end")
        if self.start_cap == "tick":
            self.draw_tick("start")
        if self.end_cap == "circle":
            self.draw_circle("end")
        if self.start_cap == "circle":
            self.draw_circle("start")

        # Draw the text
        if self.text is not None:
            qt_texture = self._generate_text_texture()
            if qt_texture:
                tid, tw, th = self._load_texture(qt_texture)
                mid_point = ScreenPoint(
                    ((line_start.x + line_end.x) / 2, (line_start.y + line_end.y) / 2)
                )
                self.draw_text(mid_point, tw, th, tid)

        # Selection highlighting
        if self.selected:
            self.draw_bounding_box()
            self.draw_handle(line_start)
            self.draw_handle(line_end)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)
