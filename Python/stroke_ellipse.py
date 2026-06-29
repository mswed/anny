import math
from OpenGL import GL

from annotations import Stroke
from utils import ImagePoint, SourceName


class EllipseStroke(Stroke):
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
        **kwargs,
    ) -> None:
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )

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

        return self._point_inside_ellipse(position)

    def _point_inside_ellipse(self, point: ImagePoint) -> bool:
        """The actual selection detection logic. Checks if the clicked point
        is inside the ellipse

        Parameters
        ----------
        position : ImagePoint
            The position the user clicked

        Returns
        -------
        bool
            True if the point is inside the ellipse else False

        """
        p = point.to_screenspace()
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        if p and start and end:
            center_x = (start.x + end.x) / 2
            center_y = (start.y + end.y) / 2
            radius_x = abs(end.x - start.x) / 2
            radius_y = abs(end.y - start.y) / 2

            if radius_x == 0 or radius_y == 0:
                return False

            dx = (p.x - center_x) / radius_x
            dy = (p.y - center_y) / radius_y

            return (dx * dx + dy * dy) <= 1.0

        return False

    def _draw_ellipse(self) -> None:
        """
        Draw a GL ellipse including fill and outline
        """
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        if not start or not end:
            return

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

        if start and end:
            self._draw_ellipse()

            # Selection highlighting
            if self.selected:
                edges = self._get_bounding_box_edges()
                if edges:
                    self._draw_bounding_box(edges)
                self._draw_handle(start)
                self._draw_handle(end)

            # Cleanup - so we don't confuse RV
            GL.glDisable(GL.GL_LINE_SMOOTH)
            GL.glDisable(GL.GL_BLEND)
            GL.glLineWidth(1.0)
