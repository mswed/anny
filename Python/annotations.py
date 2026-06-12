from collections import defaultdict, namedtuple
import math
from OpenGL import GL
import rv.commands as crv


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
        self, start, end, source, width=1.0, color=(1, 0, 0, 1), opacity=1.0
    ) -> None:
        self.start = start
        self.end = end
        self.source = source
        self.width = width
        self.color = color
        self.opacity = opacity
        self.selected = False

    @property
    def screen_start(self):
        # Convert the starting point back to event space
        return crv.imageToEventSpace(self.source, self.start)

    @property
    def screen_end(self):
        # Convert the end point back to event space
        return crv.imageToEventSpace(self.source, self.end)

    def move(self, dx, dy):
        """
        Move the annotation
        """

        sx, sy = self.start
        ex, ey = self.end

        self.start = (sx + dx, sy + dy)
        self.end = (ex + dx, ey + dy)

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

        x1, y1 = self.screen_start
        x2, y2 = self.screen_end

        # get min and max with padding
        padding = 6
        min_x = min(x1, x2) - padding
        max_x = max(x1, x2) + padding
        min_y = min(y1, y2) - padding
        max_y = max(y1, y2) + padding

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

    def draw_handle(self, x, y, size=6):
        half = size / 2

        # Square
        GL.glColor4f(1.0, 1.0, 1.0, 1.0)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(x - half, y - half)
        GL.glVertex2f(x + half, y - half)
        GL.glVertex2f(x + half, y + half)
        GL.glVertex2f(x - half, y + half)
        GL.glEnd()

        # Border
        GL.glColor4f(0, 0, 0, 1.0)
        GL.glBegin(GL.GL_LINE_LOOP)
        GL.glVertex2f(x - half, y - half)
        GL.glVertex2f(x + half, y - half)
        GL.glVertex2f(x + half, y + half)
        GL.glVertex2f(x - half, y + half)
        GL.glEnd()

    def render(self):
        pass


class LineStroke(Stroke):
    def __init__(
        self, start, end, source, width=1.0, color=(1, 0, 0, 1), opacity=1.0
    ) -> None:
        super().__init__(start, end, source, width, color, opacity)

    def __repr__(self) -> str:
        return f"<LineStroke> start: {self.start} end: {self.end} color: {self.color}"

    def render(self):
        # Antialiasing
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

        # Draw
        GL.glLineWidth(self.width)
        GL.glColor4f(self.color[0], self.color[1], self.color[2], self.opacity)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(*self.screen_start)
        GL.glVertex2f(*self.screen_end)
        GL.glEnd()

        # Selection highlighting
        if self.selected:
            self.draw_bounding_box()
            self.draw_handle(*self.screen_start)
            self.draw_handle(*self.screen_end)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)
