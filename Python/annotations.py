from collections import defaultdict
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
    def __init__(self, start, end, source, width=1.0, color=(1, 0, 0, 1)) -> None:
        self.start = start
        self.end = end
        self.source = source
        self.width = width
        self.color = color

    @property
    def screen_start(self):
        # Convert the starting point back to event space
        return crv.imageToEventSpace(self.source, self.start)

    @property
    def screen_end(self):
        # Convert the end point back to event space
        return crv.imageToEventSpace(self.source, self.end)

    def render(self):
        pass


class LineStroke(Stroke):
    def __init__(self, start, end, source, width=5.0, color=(1, 0, 0, 1)) -> None:
        super().__init__(start, end, source, width, color)

    def render(self):

        # Antialiasing
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

        # Line width
        GL.glLineWidth(self.width)

        # Draw
        GL.glColor4f(*self.color)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(*self.screen_start)
        GL.glVertex2f(*self.screen_end)
        GL.glEnd()

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)
