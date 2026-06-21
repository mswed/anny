from collections import defaultdict
import math
from typing import Optional, Tuple, NamedTuple
from OpenGL import GL
from PySide6 import QtGui
from PySide6.QtCore import Qt
import rv.commands as crv
from utils import ImagePoint, ScreenPoint, ScreenVector


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
    line_base: ScreenPoint


class LineVerts(NamedTuple):
    bottom_left: ScreenPoint
    bottom_right: ScreenPoint
    top_right: ScreenPoint
    top_left: ScreenPoint
    mid_left: ScreenPoint
    mid_right: ScreenPoint
    start_anchor: ScreenPoint
    end_anchor: ScreenPoint
    midpoint: ScreenPoint
    start_arrow: Optional[ArrowVerts]
    end_arrow: Optional[ArrowVerts]
    perp: ScreenVector
    half_offset: ScreenVector


class TickVerts(NamedTuple):
    top: ScreenPoint
    bottom: ScreenPoint


class Color(NamedTuple):
    r: float
    g: float
    b: float
    a: float


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
    """A single annotation class

    Attributes
    ----------
    start : Start point in image space
    end : End point in image space
    source : Name of the source the annotation is drawn on
    width : Stroke width
    color : Stroke color as normalized floats
    opacity : Stroke opacity
    selected : Is the stroke selected?

    """

    editable_properties = ["width", "color", "opacity", "fill_color", "fill_opacity"]

    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
        width: float = 1.0,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1.0,
        fill_color: tuple = (1, 0, 0, 1),
        fill_opacity: float = 1.0,
    ) -> None:
        self.start = start
        self.end = end
        self.source = source
        self.width = width
        self._color = color
        self._fill_color = fill_color
        self.opacity = opacity
        self.fill_opacity = fill_opacity
        self.selected = False

    @property
    def color(self):
        return Color(self._color[0], self._color[1], self._color[2], self.opacity)

    @color.setter
    def color(self, value: tuple):
        self._color = value

    @property
    def fill_color(self):
        return Color(
            self._fill_color[0],
            self._fill_color[1],
            self._fill_color[2],
            self.fill_opacity,
        )

    @fill_color.setter
    def fill_color(self, value: tuple):
        self._fill_color = value

    def get_handle_verts(self, point: ScreenPoint, size: float = 6.0) -> SquareVerts:
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

    def detect_handle_selection(self, point: ImagePoint, position: str) -> bool:
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

    def detect_selection(self, point: ImagePoint) -> bool:
        return False

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


class CircleStroke(Stroke):
    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
        width: float = 1,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1,
        fill_color: tuple = (1, 0, 0, 1),
        fill_opacity: float = 1,
        **kwargs,
    ) -> None:
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )

    def _point_inside_ellipse(self, point: ImagePoint) -> bool:
        p = point.to_screenspace()
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        center_x = (start.x + end.x) / 2
        center_y = (start.y + end.y) / 2
        radius_x = abs(end.x - start.x) / 2
        radius_y = abs(end.y - start.y) / 2

        if radius_x == 0 or radius_y == 0:
            return False
        dx = (p.x - center_x) / radius_x
        dy = (p.y - center_y) / radius_y

        return (dx * dx + dy * dy) <= 1.0

    def detect_selection(self, point: ImagePoint) -> bool:
        return self._point_inside_ellipse(point)

    def draw_circle(self) -> None:
        """
        Draw a GL circle
        """
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        center_x = (start.x + end.x) / 2
        center_y = (start.y + end.y) / 2
        radius_x = abs(end.x - start.x) / 2
        radius_y = abs(end.y - start.y) / 2

        segments = 32

        # Fill
        fill_color = self.fill_color
        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glColor4f(
            fill_color.r,
            fill_color.g,
            fill_color.b,
            fill_color.a,
        )
        GL.glVertex2f(center_x, center_y)
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            GL.glVertex2f(
                center_x + math.cos(angle) * radius_x,
                center_y + math.sin(angle) * radius_y,
            )
        GL.glEnd()

        inner_radius_x = radius_x - self.width
        inner_radius_y = radius_y - self.width

        # Stroke
        color = self.color
        GL.glBegin(GL.GL_TRIANGLE_STRIP)
        GL.glColor4f(
            color.r,
            color.g,
            color.b,
            color.a,
        )
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments

            # Draw outer border point (same as fill)
            GL.glVertex2f(
                center_x + math.cos(angle) * radius_x,
                center_y + math.sin(angle) * radius_y,
            )

            # Draw inner border point
            GL.glVertex2f(
                center_x + math.cos(angle) * inner_radius_x,
                center_y + math.sin(angle) * inner_radius_y,
            )

        GL.glEnd()

    def render(self):
        # Antialiasing
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

        start = self.start.to_screenspace()
        end = self.end.to_screenspace()
        self.draw_circle()

        # Selection highlighting
        if self.selected:
            self.draw_bounding_box()
            self.draw_handle(start)
            self.draw_handle(end)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)


class RectStroke(Stroke):
    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
        width: float = 1,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1,
        fill_color: tuple = (1, 0, 0, 1),
        fill_opacity: float = 1,
        **kwargs,
    ) -> None:
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )

    def __repr__(self) -> str:
        return f"<RectStroke> start={self.start} end={self.end} color={self.color}"

    def get_rect_verts(self, start: ScreenPoint, end: ScreenPoint) -> SquareVerts:

        bottom_left = ScreenPoint((start.x, end.y))
        bottom_right = ScreenPoint((end.x, end.y))
        top_right = ScreenPoint((end.x, start.y))
        top_left = ScreenPoint((start.x, start.y))

        return SquareVerts(bottom_left, bottom_right, top_right, top_left)

    def point_inside_stroke(self, point: ImagePoint) -> bool:
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
        verts = self.get_rect_verts(start, end)

        x_start = verts.bottom_left.x
        x_end = verts.bottom_right.x
        y_start = verts.top_left.y
        y_end = verts.bottom_left.y

        return x_end > hp.x > x_start and y_start > hp.y > y_end

    def detect_selection(self, point: ImagePoint) -> bool:
        return self.point_inside_stroke(point)

    def draw_border(self, rect: SquareVerts):

        # Top
        start = rect.top_left
        end = ScreenPoint((rect.top_right.x, rect.top_right.y - self.width))
        verts = self.get_rect_verts(start, end)
        self.draw_rect(verts, color=self.color)

        # Left
        start = rect.top_left
        end = ScreenPoint((rect.bottom_left.x + self.width, rect.bottom_left.y))
        verts = self.get_rect_verts(start, end)
        self.draw_rect(verts, color=self.color)

        # Right
        start = rect.top_right
        end = ScreenPoint((rect.bottom_right.x - self.width, rect.bottom_right.y))
        verts = self.get_rect_verts(start, end)
        self.draw_rect(verts, color=self.color)

        # Bottom
        start = rect.bottom_left
        end = ScreenPoint((rect.bottom_right.x, rect.bottom_right.y + self.width))
        verts = self.get_rect_verts(start, end)
        self.draw_rect(verts, color=self.color)

    def draw_rect(self, verts: SquareVerts, color: Color):

        # Square
        GL.glColor4f(color.r, color.g, color.b, color.a)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(*verts.bottom_left)
        GL.glVertex2f(*verts.bottom_right)
        GL.glVertex2f(*verts.top_right)
        GL.glVertex2f(*verts.top_left)
        GL.glEnd()

    def render(self):

        # Antialiasing
        # GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        # GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        verts = self.get_rect_verts(start, end)

        # Square
        GL.glColor4f(
            self.fill_color[0],
            self.fill_color[1],
            self.fill_color[2],
            self.fill_opacity,
        )
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(*verts.bottom_left)
        GL.glVertex2f(*verts.bottom_right)
        GL.glVertex2f(*verts.top_right)
        GL.glVertex2f(*verts.top_left)
        GL.glEnd()

        self.draw_border(verts)

        # Selection highlighting
        if self.selected:
            self.draw_bounding_box()
            self.draw_handle(start)
            self.draw_handle(end)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)


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
    ]

    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
        width: float = 1.0,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1.0,
        fill_color: tuple = (1, 0, 0, 1),
        fill_opacity: float = 1.0,
        start_cap: Optional[str] = None,
        end_cap: Optional[str] = None,
        text: Optional[str] = None,
    ) -> None:
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )
        self.start_cap = start_cap
        self.end_cap = end_cap
        self.text = text

    def __repr__(self) -> str:
        return f"<LineStroke> start={self.start} end={self.end} color={self.color}"

    def _point_to_stroke_distance(self, point):
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

    def detect_selection(self, point: ImagePoint) -> bool:

        # Find closest stoke to threshold
        THRESHOLD = 0.01

        dist = self._point_to_stroke_distance(point)
        return dist < THRESHOLD

    def get_line_verts(self) -> Optional[LineVerts]:
        # Figure out start and end points in screen space
        # We need to record the original start and end for the handles
        start_anchor = self.start.to_screenspace()
        end_anchor = self.end.to_screenspace()

        line_start = start_anchor
        line_end = end_anchor

        # If we have arrows the start and end shrink to the base
        # so the arrow has a point
        start_arrow = None
        end_arrow = None
        if self.start_cap == "arrow":
            start_arrow = self.get_arrow_verts(start_anchor, end_anchor, "start")
            if start_arrow:
                line_start = start_arrow.line_base
        if self.end_cap == "arrow":
            end_arrow = self.get_arrow_verts(start_anchor, end_anchor, "end")
            if end_arrow:
                line_end = end_arrow.line_base

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
            ((mid_left.x + mid_right.x) / 2, (mid_left.y + mid_right.y) / 2)
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

    def get_tick_verts(self, line: LineVerts, position="start"):

        # Create a direction vecto
        tick_width = max(self.width * 2, 1)

        # Calculate points
        base = line.mid_left if position == "start" else line.mid_right
        # base + (perp * width)
        top = base + (line.perp * tick_width)
        # base - (perp * width)
        bottom = base - (line.perp * tick_width)

        return TickVerts(top, bottom)

    def get_arrow_verts(self, start: ScreenPoint, end: ScreenPoint, position="end"):

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
        tip = (
            end + (perp * (self.width / 2))
            if position == "end"
            else start - (perp * (self.width / 2))
        )
        base = tip - (normalized * arrow_length * 2)
        left_wing = base + (perp * arrow_width)
        right_wing = base - (perp * arrow_width)

        line_tip = end if position == "end" else start
        line_base = line_tip - (normalized * arrow_length * 2)

        return ArrowVerts(tip, left_wing, right_wing, base, line_base)

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
        image.fill(
            QtGui.QColor.fromRgbF(
                self.fill_color[0],
                self.fill_color[1],
                self.fill_color[2],
                self.fill_opacity,
            )
        )

        # Paint
        painter = QtGui.QPainter(image)
        painter.setFont(font)
        painter.setPen(
            QtGui.QColor.fromRgbF(
                self.color[0], self.color[1], self.color[2], self.opacity
            )
        )
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

    def draw_line(self, verts, color):

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

    def draw_tick(self, line: LineVerts, position="start"):
        verts = self.get_tick_verts(line, position)
        if verts:
            GL.glLineWidth(self.width / 2)
            GL.glColor4f(self.color[0], self.color[1], self.color[2], self.opacity)
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(*verts.top)
            GL.glVertex2f(*verts.bottom)
            GL.glEnd()

    def draw_arrow(
        self, start: ScreenPoint, end: ScreenPoint, position: str = "end"
    ) -> None:
        verts = self.get_arrow_verts(start, end, position)
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

    def draw_circle(self, line: LineVerts, position: str) -> None:
        """
        Draw a GL circle at the start or end of the line

        Parameters
        ----------
        line : LineVerts
            The drawn line points
        position : str
            Which point should we use to draw? start or end?

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

    def draw_text(
        self, midpoint: ScreenPoint, width: float, height: float, texture_id: int
    ) -> None:
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

    def _draw_cap(
        self, cap_type: Optional[str], position: str, line: LineVerts
    ) -> None:
        if cap_type is None:
            return

        if cap_type == "arrow":
            self.draw_arrow(line.start_anchor, line.end_anchor, position)
        elif cap_type == "tick":
            self.draw_tick(line, position)
        elif cap_type == "circle":
            self.draw_circle(line, position)
        else:
            print("Unknown cap type", cap_type)

    def render(self):
        # Antialiasing
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

        verts = self.get_line_verts()
        if not verts:
            return

        self.draw_line(verts, self.color)

        # Draw the caps
        self._draw_cap(self.start_cap, "start", verts)
        self._draw_cap(self.end_cap, "end", verts)

        # Draw the text
        if self.text:
            qt_texture = self._generate_text_texture()
            if qt_texture:
                tid, tw, th = self._load_texture(qt_texture)
                self.draw_text(verts.midpoint, tw, th, tid)

        # Selection highlighting
        if self.selected:
            self.draw_bounding_box()
            self.draw_handle(verts.start_anchor + verts.half_offset)
            self.draw_handle(verts.end_anchor + verts.half_offset)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)
