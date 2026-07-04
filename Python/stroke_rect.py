from OpenGL import GL

from annotations import Stroke
from utils import ImagePoint, ScreenPoint, Source, RectEdges, Color


class RectStroke(Stroke):
    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: Source,
        width: float = 1,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1,
        fill_color: tuple = (1, 1, 1, 1),
        fill_opacity: float = 1,
        **kwargs,
    ) -> None:
        """Create a rectangle storke

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
        **kwargs
            Any additional kwargs the caller might pass (at the moment all are ignored)

        """
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )

    def __repr__(self) -> str:
        return f"<RectStroke> start={self.start} end={self.end} color={self.color}"

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

        return self._point_inside_stroke(position)

    def _get_rect_edges(self, start: ScreenPoint, end: ScreenPoint) -> RectEdges:

        left = min(start.x, end.x)
        right = max(start.x, end.x)
        top = max(start.y, end.y)
        bottom = min(start.y, end.y)

        return RectEdges(left, right, top, bottom)

    def _point_inside_stroke(self, point: ImagePoint) -> bool:
        """The actual selection detection logic. Checks if the clicked point
        is inside the rect

        Parameters
        ----------
        position : ImagePoint
            The position the user clicked

        Returns
        -------
        bool
            True if the point is inside the rect else False

        """

        hp = point.to_screenspace()
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        if hp and start and end:
            edges = self._get_rect_edges(start, end)

            return edges.right > hp.x > edges.left and edges.top > hp.y > edges.bottom
        return False

    def _draw_outline(self, rect: RectEdges):
        """Draw the outline of the rectangle which is is made out of 4 other
        rectangles. The outline is drawn inwards from the original size of the rectangle

        Parameters
        ----------
        rect : RectEdges
            The edges of the rectangle

        """
        # Top
        start = rect.top_left
        end = ScreenPoint(rect.top_right.x, rect.top_right.y - self.width)
        edges = self._get_rect_edges(start, end)
        self._draw_rect(edges, color=self.color)

        # Left
        start = rect.top_left
        end = ScreenPoint(rect.bottom_left.x + self.width, rect.bottom_left.y)
        edges = self._get_rect_edges(start, end)
        self._draw_rect(edges, color=self.color)

        # Right
        start = rect.top_right
        end = ScreenPoint(rect.bottom_right.x - self.width, rect.bottom_right.y)
        edges = self._get_rect_edges(start, end)
        self._draw_rect(edges, color=self.color)

        # Bottom
        start = rect.bottom_left
        end = ScreenPoint(rect.bottom_right.x, rect.bottom_right.y + self.width)
        edges = self._get_rect_edges(start, end)
        self._draw_rect(edges, color=self.color)

    def _draw_rect(self, edges: RectEdges, color: Color):
        """Draw a rectangle. This is used to both draw the fill rectangle and the outlines

        Parameters
        ----------
        edges : RectEdges
            Edges of rectangle to draw
        color : Color
            Color in rgba format

        """
        # Square
        GL.glColor4f(color.r, color.g, color.b, color.a)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(*edges.bottom_left)
        GL.glVertex2f(*edges.bottom_right)
        GL.glVertex2f(*edges.top_right)
        GL.glVertex2f(*edges.top_left)
        GL.glEnd()

    def render(self):

        # Antialiasing
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        start = self.start.to_screenspace()
        end = self.end.to_screenspace()
        if start and end:
            edges = self._get_rect_edges(start, end)

            self._draw_rect(edges, self.fill_color)
            # Fill

            # Outline
            self._draw_outline(edges)

            # Selection highlighting
            if self.selected:
                self._draw_bounding_box(edges)
                self._draw_handle(start)
                self._draw_handle(end)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)
