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
    def __init__(self, start, end, source, color=(1, 0, 0, 1)) -> None:
        self.start = start
        self.end = end
        self.source = source
        self.color = color

    def render(self):
        pass


class LineStroke(Stroke):
    def __init__(self, start, end, source, color=(1, 0, 0, 1)) -> None:
        super().__init__(start, end, source, color)

    def render(self):

        # We need to convert back to event space
        screen_start = crv.imageToEventSpace(self.source, self.start)
        screen_end = crv.imageToEventSpace(self.source, self.end)

        GL.glColor4f(*self.color)
        GL.glBegin(GL.GL_LINES)
        GL.glVertex2f(*screen_start)
        GL.glVertex2f(*screen_end)
        GL.glEnd()
