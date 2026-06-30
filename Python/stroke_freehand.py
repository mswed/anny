from typing import Optional
import math
from OpenGL import GL

from annotations import Stroke
from utils import ImagePoint, ScreenPoint, SourceName, RectEdges, Color, QuadCorners


class FreehandStroke(Stroke):
    editable_properties = [
        "width",
        "color",
        "opacity",
        "smoothing",
    ]

    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: SourceName,
        width: float = 1,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1,
        smoothing: int = 0,
        **kwargs,
    ) -> None:
        """Create a free hand line

        Parameters
        ----------
        start : ImagePoint
            The first point in the stroke
        end : ImagePoint
            The last point in the storke. On init this should match start
        source : SourceName
            The name of the source the stroke is attached to
        width : float
            The line width
        color : tuple
            The line color
        opacity : float
            The line opacity
        smoothing : int
           The amount of smothing to apply to the line
        **kwargs
            Any additional kwargs the caller might pass (at the moment all are ignored)

        """
        super().__init__(
            start,
            end,
            source,
            width,
            color,
            opacity,
        )
        self.points = [start]
        self._smooth_points = []
        self._smoothing = smoothing

    @property
    def smoothing(self) -> int:
        """The number of smoothing iterations of the line

        Returns
        -------
        int
            The number of smoothing iterations

        """
        return self._smoothing

    @smoothing.setter
    def smoothing(self, value: int):
        """Set the number of smoothing iterations to run on the line

        Parameters
        ----------
        value : int
            Number of iterations

        """
        # Clear the point cache
        self._smooth_points = []
        self._smoothing = value

    @property
    def smooth_points(self) -> list:
        """Get the list of smooth points

        Returns
        -------
        list
            List of smooth points

        """
        if not self._smooth_points:
            self._smooth_points = self._get_smooth_points(self.points, self.smoothing)

        return self._smooth_points

    def update_draw(self, new_position: ImagePoint):
        """Update the point list and end point of the stroke. Called during drawing
        A new point is created only if it's far enough from the last point so we don't end up
        with an insane number of points

        Parameters
        ----------
        new_position : ImagePoint
            The current position of the mouse

        """

        if self.points:
            last = self.points[-1]
            # Check how far our last point is from the last point
            # We don't bother with getting the root to make it a bit faster
            distance_squared = new_position.distance_to_squared(last)

            MIN_DIST = 0.009
            if distance_squared < MIN_DIST**2:
                # The point is too close, ignore it
                return

        self.points.append(new_position)
        self.end = new_position
        self._smooth_points = []

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
        return self._detect_line_selection(position)

    def _get_smooth_points(
        self, points: list[ImagePoint], iterations: int
    ) -> list[ImagePoint]:
        """Smooth the line's points

        Parameters
        ----------
        points : list[ImagePoint]
            Points to smooth
        iterations : int
            Number of smothing iterations the higher the number the smoother the line (and the slower the render)

        Returns
        -------
        list[ImagePoint]
            New list of points representing the smooth line

        """
        for _ in range(iterations):
            new_points = [points[0]]
            for i in range(len(points) - 1):
                a = points[i]
                b = points[i + 1]
                q = a.lerp(b, 0.25)
                r = a.lerp(b, 0.75)
                new_points.append(q)
                new_points.append(r)

            new_points.append(points[-1])
            points = new_points

        return points

    def _detect_line_selection(self, position: ImagePoint) -> bool:
        """The actual selection detection logic. Checks if the clicked point
        is close enough to any of the line segments

        Parameters
        ----------
        position : ImagePoint
            The position the user clicked

        Returns
        -------
        bool
            True if the position is close enough to any of the line segments else False

        """
        THRESHOLD = 0.01
        for i in range(1, len(self.smooth_points)):
            start = self.smooth_points[i - 1]
            end = self.smooth_points[i]
            dist = self._point_to_stroke_distance(start, end, position)
            if dist < THRESHOLD:
                return True

        return False

    def _get_bounding_box_edges(self) -> Optional[RectEdges]:
        """
        Get the bounding box edges. We need to override the parent since we have
        more than just start and end

        Returns
        -------
        RectEdges
            The edges of the bounding box

        """
        if not self.points:
            return

        ss_points = [p.to_screenspace() for p in self.points]
        xs = [p.x for p in ss_points if p is not None]
        ys = [p.y for p in ss_points if p is not None]

        # get min and max with padding
        left = min(xs)
        right = max(xs)
        top = max(ys)
        bottom = min(ys)

        return RectEdges(left, right, top, bottom)

    def _move(self, dx: float, dy: float, move_type=None):
        """Move the annotation or one of its points. All movement is calcualted in image space

        Parameters
        ----------
        dx : float
            Delta between original point and new point
        dy : float
            Delta between original point and new point
        """

        for p in self.points:
            p.move(dx, dy)

        # Update the stroke's points
        self.start = self.points[0]
        self.end = self.points[-1]
        self._smooth_points = []

    def _get_segment_corners(
        self, start: ScreenPoint, end: ScreenPoint
    ) -> Optional[QuadCorners]:
        """Get the corner verts of a line segment. We get corners instead of edges
        since the segment is not axis aligned (i.e. rotated)

        Parameters
        ----------
        start : ScreenPoint
            The segment start point
        end : ScreenPoint
            The segment end point

        Returns
        -------
        Optional[QuadCorners]
            The line verts if we are able to calculate it

        """
        direction = start.direction_to(end)
        normalized = direction.normalized
        if normalized is None:
            return

        perp = normalized.perpendicular
        offset = perp * (self.width / 2)

        bottom_left = start - offset
        bottom_right = end - offset
        top_right = end + offset
        top_left = start + offset

        return QuadCorners(bottom_left, bottom_right, top_right, top_left)

    def _draw_segment(self, verts: QuadCorners, color: Color):
        """Draw a line segment

        Parameters
        ----------
        verts : QuadCorners
            The segment's verts
        color : Color
            The segment's color

        """
        # Square
        GL.glColor4f(color.r, color.g, color.b, color.a)
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(*verts.bottom_left)
        GL.glVertex2f(*verts.bottom_right)
        GL.glVertex2f(*verts.top_right)
        GL.glVertex2f(*verts.top_left)
        GL.glEnd()

    def _draw_joint(self, center: ScreenPoint) -> None:
        """
        Draw a GL circle at a point to smooth the line

        Parameters
        ----------
        center : ScreenPoint
            The point to draw the circle around. It shoud match the end or start of the segment
        """
        segments = 12
        radius = self.width / 2

        GL.glBegin(GL.GL_TRIANGLE_FAN)
        GL.glVertex2f(*center)
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            GL.glVertex2f(
                center.x + math.cos(angle) * radius, center.y + math.sin(angle) * radius
            )
        GL.glEnd()

    def render(self):
        # Antialiasing
        GL.glEnable(GL.GL_POLYGON_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glHint(GL.GL_LINE_SMOOTH_HINT, GL.GL_NICEST)

        # Draw a line
        if len(self.points) > 1:
            points = self.smooth_points
            for i in range(1, len(points)):
                start = points[i - 1].to_screenspace()
                end = points[i].to_screenspace()
                verts = self._get_segment_corners(start, end)
                if verts:
                    self._draw_segment(verts, self.color)

            for p in points:
                point = p.to_screenspace()
                self._draw_joint(point)

        # Selection highlighting
        if self.selected:
            edges = self._get_bounding_box_edges()
            if edges:
                self._draw_bounding_box(edges)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_POLYGON_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)
