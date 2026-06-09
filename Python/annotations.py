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
    def __init__(self, start, end, color=(1, 0, 0, 1)) -> None:
        self.start = start
        self.end = end
        self.color = color

    def render(self):
        pass


class LineStroke(Stroke):
    def __init__(self, start, end, color=(1, 0, 0, 1)) -> None:
        super().__init__(start, end, color)

    def render(self):
        GL.glColor4f(*self.color)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(*self.start)
        GL.glVertex2f(*self.end)
        GL.glEnd()
