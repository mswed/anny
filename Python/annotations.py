from __future__ import annotations
from collections import defaultdict
import math
from typing import Optional, Tuple
from OpenGL import GL
from PySide6 import QtGui
from PySide6.QtCore import Qt
import rv.commands as crv
from utils import (
    ImagePoint,
    ScreenPoint,
    RectEdges,
    QuadCorners,
    ArrowVerts,
    LineVerts,
    TickVerts,
    Color,
    SourceName,
    SourceNode,
)


class SourceAnnotations:
    """Store a source strokes against frames

    Attributes
    ----------
    frames : Frame dictionary. Each frame contains a list of strokes
    """

    def __init__(self) -> None:
        self.frames: dict[int, list[Stroke]] = defaultdict(list)

    @property
    def annotated_frames(self) -> list:
        """A sorted list of frames with strokes

        Returns
        -------
        list
            Sorted list of frame numbers

        """
        return sorted(list(self.frames.keys())) if self.frames else []

    def add(self, frame: int, stroke: Stroke):
        """Add a a stroke to the specified frame

        Parameters
        ----------
        frame : int
            The frame the stroke is on
        stroke : Stroke
            The stroke data

        """
        self.frames[frame].append(stroke)

    def remove(self, frame: int, stroke: Stroke):
        """Remove a stroke from the specified frame

        Parameters
        ----------
        frame : int
            Frame to remove the stroke from
        stroke : Stroke
            The stroke reference

        """
        self.frames[frame].remove(stroke)

    def strokes_at_frame(self, frame: int) -> list:
        """Get all of the sources strokes at the specified frame

        Parameters
        ----------
        frame : int
            Frame to look for

        Returns
        -------
        list
            The list of stroke for that frame

        """
        return self.frames.get(frame, [])

    def clear_frame(self, frame: int):
        """Remove all strokes from the specified frame

        Parameters
        ----------
        frame : int
            The frame to remove the strokes from

        """
        self.frames[frame] = []

    def next_annotated_frame(self, current_frame: int) -> Optional[int]:
        """Search forward for the next frame that has annotations on it

        Parameters
        ----------
        current_frame : int
            The current frame the first annotated frame that is larger is our next frame

        Returns
        -------
        Optional[int]
            Frame number if a next frame is found None otherwise

        """
        frames = self.annotated_frames
        if not frames:
            return

        for i in range(len(frames)):
            if frames[i] > current_frame:
                return frames[i]

        return frames[0]

    def previous_annotated_frame(self, current_frame: int) -> Optional[int]:
        """Search backward for the previous frame that has annotations on it

        Parameters
        ----------
        current_frame : int
            The current frame the first annotated frame that is smaller is our next frame

        Returns
        -------
        Optional[int]
            Frame number if a previous frame is found None otherwise

        """
        frames = self.annotated_frames
        if not frames:
            return

        for i in range(len(frames) - 1, -1, -1):
            if frames[i] < current_frame:
                return frames[i]

        return frames[-1]


class AnnotationLayer:
    """
    The base class that renders the actual annotations. Annotations are added to the sources dict and then
    rendered via the stroke's render function

    Attributes
    ----------
    sources : The sources in the session. The source name is the source node

    """

    def __init__(self) -> None:
        self.sources: dict[str, SourceAnnotations] = defaultdict(SourceAnnotations)

    def add_stroke(self, source: SourceNode, frame: int, stroke: Stroke):
        """Add a stroke to the layer

        Parameters
        ----------
        source : SourceNode
            The sources node to add the stroke to
        frame : int
            The frame to add the stroke to
        stroke : Stroke
            The stroke data
        """

        self.sources[source].add(frame, stroke)

    def delete_stroke(self, source: SourceNode, frame: int, stroke: Stroke):
        """Delete a stroke from the layer

        Parameters
        ----------
        source : SourceNode
            The sources node to add the stroke to
        frame : int
            The frame to add the stroke to
        stroke : Stroke
            The stroke data
        """

        self.sources[source].remove(frame, stroke)

    def clear_frame(self, source: SourceNode, frame: int):
        """Delete all annotations on the frame

        Parameters
        ----------
        source : SourceNode
            The sources node to add the stroke to
        frame : int
            The frame to add the stroke to
        """
        self.sources[source].clear_frame(frame)

    def get_next_frame(self, source: SourceNode, current_frame: int) -> Optional[int]:
        """Get the next annotated frame

        Parameters
        ----------
        source : SourceNode
            The source node to search for
        current_frame : int
            The current frame

        Returns
        -------
        Optional[int]
            Next annotated from number if one is found, else None

        """
        return self.sources[source].next_annotated_frame(current_frame)

    def get_previous_frame(
        self, source: SourceNode, current_frame: int
    ) -> Optional[int]:
        """Get the previous annotated frame

        Parameters
        ----------
        source : SourceNode
            The source node to search for
        current_frame : int
            The current frame

        Returns
        -------
        Optional[int]
            Previous annotated from number if one is found, else None

        """
        return self.sources[source].previous_annotated_frame(current_frame)

    def get_annotated_frames(self, source: SourceNode) -> list:
        """Get a sorted list of all annotated frames on the source

        Parameters
        ----------
        source : SourceNode
            The source name

        Returns
        -------
        list
            A sorted list of all annotated frames on the source

        """
        return self.sources[source].annotated_frames

    def capture_frame_buffer(self, event) -> QtGui.QImage:
        """Capture the current frame as a QImage

        Parameters
        ----------
        event : Event
            The RV event that triggered the capture

        Returns
        -------
        QtGui.QImage
            The captured viewport

        """
        # Get viewport size
        w, h = event.domain()

        # Get the buffer
        buffer = GL.glReadPixels(0, 0, w, h, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)

        # Convert it to an image
        image = QtGui.QImage(buffer, w, h, QtGui.QImage.Format_RGBA8888)

        # Flip it vertically
        image = image.mirrored(False, True)

        return image

    def render(self, event):
        """Render all of the strokes on all of the sources in the layer

        Parameters
        ----------
        event : Event
            The internal RV event that triggered the render

        """
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

        # TODO: We should probably only render the first source using renderedSources
        for source in self.sources.values():
            for stroke in source.strokes_at_frame(frame):
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
        fill_color: tuple = (1, 1, 1, 1),
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
        self.editing = True

    # ############################################################################
    # PUBLIC INTERFACE
    # ############################################################################
    @property
    def color(self) -> Color:
        """Get the stroke's color

        Returns
        -------
        Color
            The stroke's color

        """
        return Color(self._color[0], self._color[1], self._color[2], self.opacity)

    @color.setter
    def color(self, value: tuple):
        """Set the stroke's color

        Parameters
        ----------
        value : tuple
            RGBA values for the stroke

        """
        self._color = value

    @property
    def fill_color(self) -> Color:
        """Get the stroke's fill color

        Returns
        -------
        Color
            The stroke's fill color

        """

        return Color(
            self._fill_color[0],
            self._fill_color[1],
            self._fill_color[2],
            self.fill_opacity,
        )

    @fill_color.setter
    def fill_color(self, value: tuple):
        """Set the stroke's fill color

        Parameters
        ----------
        value : tuple
            RGBA values for the stroke
        """

        self._fill_color = value

    def move(self, dx: float, dy: float, move_type: str = "stroke"):
        """Move the annotation or one of its points. All movement is calcualted in image space

        Parameters
        ----------
        dx : float
            Delta between original point and new point
        dy : float
            Delta between original point and new point
        move_type : str
            What are we moving? stroke, start or end?
        """

        self._move(dx, dy, move_type)

    def detect_selection(self, position: ImagePoint) -> bool:
        """Subclasses need to implement this to detect stroke selection

        Parameters
        ----------
        position : ImagePoint
            The position of the mouse click

        Returns
        -------
        bool
            True if selected, False otherwise

        """
        return False

    def update_draw(self, new_position: ImagePoint):
        """Update the end point of the stroke. Called during drawing

        Parameters
        ----------
        new_position : ImagePoint
            The current position of the mouse

        """
        self.end.x = new_position.x
        self.end.y = new_position.y

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
            True if handle was clicked False otherwise
        """

        # Handles are drawn in screen space, so convert to event space first
        hp = point.to_screenspace()
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        if hp and start and end:
            if position == "start":
                handle_verts = self._get_handle_verts(start)
            else:
                handle_verts = self._get_handle_verts(end)

            x_start = handle_verts.bottom_left.x
            x_end = handle_verts.bottom_right.x
            y_start = handle_verts.top_left.y
            y_end = handle_verts.bottom_left.y

            return x_end > hp.x > x_start and y_start > hp.y > y_end

        return False

    # ############################################################################
    # PRIVATE INTERFACE
    # ############################################################################
    def _point_to_stroke_distance(
        self, stroke_start: ImagePoint, stroke_end: ImagePoint, point: ImagePoint
    ) -> float:
        """
        Calculate the distance from the mouse click to the stroke. Used for selection.

        Parameters
        ----------
        stroke_start : ImagePoint
            The start of the stroke
        stroke_end : ImagePoint
            The end of the stroke
        point : ImagePoint
            The point to check against (where the user clicked)

        Returns
        -------
        float
            The distance between the click and the stroke

        """
        # Calculate stroke length
        dx = stroke_end.x - stroke_start.x
        dy = stroke_end.y - stroke_start.y

        if dx == 0 and dy == 0:
            # Our stroke has no length, it's a dot. Measure the distance to start instead
            return point.distance_to(stroke_start)

        # Find the point on the actual stroke that is closest to our click
        t = ((point.x - stroke_start.x) * dx + (point.y - stroke_start.y) * dy) / (
            dx * dx + dy * dy
        )
        # Clamp it so it only applies to the actual stroke
        t = max(0, min(1, t))

        nearest = ImagePoint(stroke_start.x + t * dx, stroke_start.y + t * dy)

        return point.distance_to(nearest)

    def _move(self, dx: float, dy: float, move_type: str = "stroke"):
        """Move the annotation or one of its points. All movement is calcualted in image space

        Parameters
        ----------
        dx : float
            Delta between original point and new point
        dy : float
            Delta between original point and new point
        move_type : str
            What are we moving? stroke, start or end?
        """

        if move_type == "stroke" or move_type == "start":
            self.start.move(dx, dy)
        if move_type == "stroke" or move_type == "end":
            self.end.move(dx, dy)

    def _get_handle_verts(self, point: ScreenPoint, size: float = 6.0) -> RectEdges:
        """Get the verts of a handle so we can draw it

        Parameters
        ----------
        point : ScreenPoint
            The center point of the handle
        size : float
            The width and height of the handle

        Returns
        -------
        RectEdges
            The edges of the handle

        """
        half = size / 2

        left = point.x - half
        right = point.x + half
        top = point.y + half
        bottom = point.y - half

        return RectEdges(left, right, top, bottom)

    def _get_bounding_box_edges(self) -> Optional[RectEdges]:
        """Get the stroke's bounding box edges so we can draw it

        Returns
        -------
        Optional[RectEdges]
            The edges of the bounding box if we are able to calcualte them else None

        """
        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        if start and end:
            # get min and max
            left = min(start.x, end.x)
            right = max(start.x, end.x)
            top = max(start.y, end.y)
            bottom = min(start.y, end.y)

            return RectEdges(left, right, top, bottom)

    def _draw_handle(self, point: ScreenPoint):
        """Draw a control handle around a point

        Parameters
        ----------
        point : ScreenPoint
            The point to draw the handle around

        """
        e = self._get_handle_verts(point)
        # Square
        GL.glColor4f(1.0, 1.0, 1.0, 1.0)
        GL.glBegin(GL.GL_QUADS)
        for corner in e.corners:
            GL.glVertex2f(corner.x, corner.y)
        GL.glEnd()

        # Border
        GL.glColor4f(0, 0, 0, 1.0)
        GL.glBegin(GL.GL_LINE_LOOP)
        for corner in e.corners:
            GL.glVertex2f(corner.x, corner.y)
        GL.glEnd()

    def _draw_bounding_box(self, edges: RectEdges, padding: int = 6):
        """Draw a box around the annotation to mark a selection

        Parameters
        ----------
        edges : RectEdges
            The bounding box edges to draw
        padding : int
            Padding to add to the box

        """
        edges = edges.padded(padding)
        GL.glEnable(GL.GL_LINE_STIPPLE)
        GL.glLineStipple(1, 0xF0F0)
        GL.glLineWidth(1.0)
        GL.glColor4f(1.0, 1.0, 1.0, 0.8)

        GL.glBegin(GL.GL_LINE_LOOP)
        for corner in edges.corners:
            GL.glVertex2f(corner.x, corner.y)
        GL.glEnd()

        GL.glDisable(GL.GL_LINE_STIPPLE)

    def render(self):
        pass


class TextStroke(Stroke):
    editable_properties = [
        "width",
        "color",
        "opacity",
        "fill_color",
        "fill_opacity",
        "text",
        "font",
    ]

    MARGIN = 8

    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
        width: float = 1,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1,
        fill_color: tuple = (1, 1, 1, 1),
        fill_opacity: float = 1,
        text: Optional[str] = None,
        font: QtGui.QFont = QtGui.QFont("Arial", 14),
        **kwargs,
    ) -> None:
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )
        self.text = text
        self.font = font

    def __repr__(self) -> str:
        return f"<TextStroke> start={self.start} end={self.end} color={self.color}"

    def detect_selection(self, point: ImagePoint) -> bool:
        return self._point_inside_stroke(point)

    def _draw_text(self, edges: RectEdges, texture_id: int) -> None:
        # Enable and bind
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)

        GL.glBegin(GL.GL_QUADS)
        GL.glColor4f(1.0, 1.0, 1.0, self.opacity)
        # Map texture points to relative points
        GL.glTexCoord2f(0, 1)  # Bottom left
        GL.glVertex2f(*edges.bottom_left)
        GL.glTexCoord2f(1, 1)  # Bottom right
        GL.glVertex2f(*edges.bottom_right)
        GL.glTexCoord2f(1, 0)  # Top right
        GL.glVertex2f(*edges.top_right)
        GL.glTexCoord2f(0, 0)  # Top left
        GL.glVertex2f(*edges.top_left)
        GL.glEnd()

        # Cleanup
        GL.glDisable(GL.GL_TEXTURE_2D)

    def _get_rect_edges(self, start: ScreenPoint, end: ScreenPoint) -> RectEdges:

        # Most values come from the original drag
        left = min(start.x, end.x)
        right = max(start.x, end.x)
        top = max(start.y, end.y)

        # But the height is calcualted based on either the drag or the size
        # of the text
        height = self._get_rect_height()
        bottom = top - height

        return RectEdges(left, right, top, bottom)

    def _point_inside_stroke(self, point: ImagePoint) -> bool:
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

        edges = self._get_rect_edges(start, end)

        return edges.right > hp.x > edges.left and edges.top > hp.y > edges.bottom

    def _draw_rect(self, edges: RectEdges, color: Color):

        # Square
        GL.glColor4f(color.r, color.g, color.b, color.a)
        GL.glBegin(GL.GL_QUADS)
        for corner in edges.corners:
            GL.glVertex2f(*corner)
        GL.glEnd()

    def _get_rect_height(self) -> int:
        """
        Get the height of the box containing the text. The minimal height (while editing) is what the user drew.
        Once editing is done the height snaps to match the actual height of the text.

        Returns
        -------
        The height of the box as an int. If there's text this value includes the margins as well
        """

        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        # The height as set by the user
        dragged_height = abs(end.y - start.y)

        if not self.text:
            return dragged_height

        # The width is set by the user drawing the rect. But we add the margins to it
        # so text wrapping works correctly
        width = max(int(abs(end.x - start.x) - 2 * self.MARGIN), 1)

        # We have text measure it to determine height
        metrics = QtGui.QFontMetrics(self.font)
        flags = Qt.TextWordWrap | Qt.AlignLeft
        # We calculate the inset width for correct text wrapping
        rect = metrics.boundingRect(0, 0, int(width), 10000, flags, self.text)
        # We add the margins to the height
        text_height = rect.height() + 2 * self.MARGIN

        if self.editing:
            # As long as we're editing the height can only extend, never shrink
            return max(dragged_height, text_height)

        else:
            # we are done editing use the text height even if it means shrinking
            return text_height

    def _generate_text_texture(self) -> Optional[QtGui.QImage]:
        """Generate a text texture so we can render it using OpenGL

        Returns
        -------
        Optional[QtGui.QImage]
            The texture image
        """
        if not self.text:
            return

        # Margins
        width = abs(self.end.to_screenspace().x - self.start.to_screenspace().x)
        width = max(int(width - 2 * self.MARGIN), 1)
        # get rect height gives us the height of the rect WITH margins
        # so we remove them to get the proper padding
        height = max(self._get_rect_height() - 2 * self.MARGIN, 1)

        # Create the image
        image = QtGui.QImage(width, height, QtGui.QImage.Format_RGBA8888)
        # The actual fill comes from the drawn rect
        image.fill(Qt.transparent)

        # Paint
        painter = QtGui.QPainter(image)
        painter.setFont(self.font)
        r, g, b, a = self.color
        painter.setPen(QtGui.QColor.fromRgbF(r, g, b, a))

        flags = Qt.TextWordWrap | Qt.AlignLeft

        painter.drawText(image.rect(), flags, self.text)
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
            texture id, texture width, texture height

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

    def render(self):

        # Antialiasing
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        start = self.start.to_screenspace()
        end = self.end.to_screenspace()

        e = self._get_rect_edges(start, end)

        # Square
        r, g, b, a = self.fill_color
        GL.glColor4f(r, g, b, a)
        GL.glBegin(GL.GL_QUADS)
        for corner in e.corners:
            GL.glVertex2f(corner.x, corner.y)
        GL.glEnd()

        # # Draw the text
        if self.text:
            qt_texture = self._generate_text_texture()
            if qt_texture:
                tid, tw, th = self._load_texture(qt_texture)
                self._draw_text(e.inset(self.MARGIN), tid)

        # Selection highlighting
        if self.selected:
            self._draw_bounding_box(e)
            self._draw_handle(start)
            self._draw_handle(end)

        # Cleanup - so we don't confuse RV
        GL.glDisable(GL.GL_LINE_SMOOTH)
        GL.glDisable(GL.GL_BLEND)
        GL.glLineWidth(1.0)


class FreehandStroke(Stroke):
    editable_properties = [
        "width",
        "color",
        "opacity",
        "fill_color",
        "fill_opacity",
        "smoothing",
    ]

    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
        width: float = 1,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1,
        fill_color: tuple = (1, 1, 1, 1),
        fill_opacity: float = 1,
        smoothing=0,
        **kwargs,
    ) -> None:
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )
        self.points = [start]
        self._smooth_points = []
        self._smoothing = smoothing

    @property
    def smoothing(self):
        return self._smoothing

    @smoothing.setter
    def smoothing(self, value):
        self._smooth_points = []
        self._smoothing = value

    @property
    def smooth_points(self) -> list:
        if not self._smooth_points:
            self._smooth_points = self._get_smooth_points(self.points, self.smoothing)

        return self._smooth_points

    def update_draw(self, point: ImagePoint):

        if self.points:
            last = self.points[-1]
            # Check how far our last point is from the last point
            # We don't bother with getting the root to make it a bit faster
            distance_squared = point.distance_to_squared(last)

            MIN_DIST = 0.009
            if distance_squared < MIN_DIST**2:
                # The point is too close, ignore it
                return

        self.points.append(point)
        self.end = point
        self._smooth_points = []

    def detect_selection(self, point: ImagePoint) -> bool:
        return self._detect_line_selection(point)

    def _get_smooth_points(self, points, iterations):
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

    def _detect_line_selection(self, point: ImagePoint):
        THRESHOLD = 0.01
        for i in range(1, len(self.smooth_points)):
            start = self.smooth_points[i - 1]
            end = self.smooth_points[i]
            dist = self._point_to_stroke_distance(start, end, point)
            if dist < THRESHOLD:
                return True

        return False

    def _get_bounding_box_edges(self) -> Optional[RectEdges]:
        """
        Get the bounding box edges. We need to override the parent since we have
        more than just start and end

        Parameters
        ----------
        padding : int
            Rect padding

        Returns
        -------
        RectEdges
            The edges of the rectangle

        """
        if not self.points:
            return

        xs = [p.to_screenspace().x for p in self.points]
        ys = [p.to_screenspace().y for p in self.points]

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

        self.start = self.points[0]
        self.end = self.points[-1]
        self._smooth_points = []

    def _get_segment_corners(
        self, start: ScreenPoint, end: ScreenPoint
    ) -> Optional[QuadCorners]:

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
            The point to draw the circle around
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


class CircleStroke(Stroke):
    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
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

    def _draw_circle(self) -> None:
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
        self._draw_circle()

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


class RectStroke(Stroke):
    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
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

    def __repr__(self) -> str:
        return f"<RectStroke> start={self.start} end={self.end} color={self.color}"

    def detect_selection(self, point: ImagePoint) -> bool:
        return self._point_inside_stroke(point)

    def _get_rect_edges(self, start: ScreenPoint, end: ScreenPoint) -> RectEdges:

        left = min(start.x, end.x)
        right = max(start.x, end.x)
        top = max(start.y, end.y)
        bottom = min(start.y, end.y)

        return RectEdges(left, right, top, bottom)

    def _point_inside_stroke(self, point: ImagePoint) -> bool:
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
        edges = self._get_rect_edges(start, end)

        return edges.right > hp.x > edges.left and edges.top > hp.y > edges.bottom

    def _draw_border(self, rect: RectEdges):

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

        edges = self._get_rect_edges(start, end)

        # Square
        GL.glColor4f(
            self.fill_color[0],
            self.fill_color[1],
            self.fill_color[2],
            self.fill_opacity,
        )
        GL.glBegin(GL.GL_QUADS)
        GL.glVertex2f(*edges.bottom_left)
        GL.glVertex2f(*edges.bottom_right)
        GL.glVertex2f(*edges.top_right)
        GL.glVertex2f(*edges.top_left)
        GL.glEnd()

        self._draw_border(edges)

        # Selection highlighting
        if self.selected:
            self._draw_bounding_box(edges)
            self._draw_handle(start)
            self._draw_handle(end)

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
        "font",
    ]

    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: str,
        width: float = 1.0,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1.0,
        fill_color: tuple = (1, 1, 1, 1),
        fill_opacity: float = 1.0,
        start_cap: Optional[str] = None,
        end_cap: Optional[str] = None,
        text: Optional[str] = None,
        font: QtGui.QFont = QtGui.QFont("Arial", 14),
        **kwargs,
    ) -> None:
        super().__init__(
            start, end, source, width, color, opacity, fill_color, fill_opacity
        )
        self.start_cap = start_cap
        self.end_cap = end_cap
        self.text = text
        self.font = font

    def __repr__(self) -> str:
        return f"<LineStroke> start={self.start} end={self.end} color={self.color}"

    def detect_selection(self, point: ImagePoint) -> bool:
        return self._detect_line_selection(point)

    def _detect_line_selection(self, point: ImagePoint):
        # Find closest stoke to threshold
        THRESHOLD = 0.01

        dist = self._point_to_stroke_distance(self.start, self.end, point)
        return dist < THRESHOLD

    def _get_line_verts(self) -> Optional[LineVerts]:
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
            start_arrow = self._get_arrow_verts(start_anchor, end_anchor, "start")
            if start_arrow:
                line_start = start_arrow.line_base
        if self.end_cap == "arrow":
            end_arrow = self._get_arrow_verts(start_anchor, end_anchor, "end")
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

    def _get_tick_verts(self, line: LineVerts, position="start"):

        # Create a direction vecto
        tick_width = max(self.width * 2, 1)

        # Calculate points
        base = line.mid_left if position == "start" else line.mid_right
        # base + (perp * width)
        top = base + (line.perp * tick_width)
        # base - (perp * width)
        bottom = base - (line.perp * tick_width)

        return TickVerts(top, bottom)

    def _get_arrow_verts(self, start: ScreenPoint, end: ScreenPoint, position="end"):

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
                self.fill_color[0],
                self.fill_color[1],
                self.fill_color[2],
                self.fill_opacity,
            )
        )

        # Paint
        painter = QtGui.QPainter(image)
        painter.setFont(self.font)
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

    def _draw_line(self, verts, color):

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

    def _draw_tick(self, line: LineVerts, position="start"):
        verts = self._get_tick_verts(line, position)
        if verts:
            GL.glLineWidth(self.width / 2)
            GL.glColor4f(self.color[0], self.color[1], self.color[2], self.opacity)
            GL.glBegin(GL.GL_LINES)
            GL.glVertex2f(*verts.top)
            GL.glVertex2f(*verts.bottom)
            GL.glEnd()

    def _draw_arrow(
        self, start: ScreenPoint, end: ScreenPoint, position: str = "end"
    ) -> None:
        verts = self._get_arrow_verts(start, end, position)
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

    def _draw_text(
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
            self._draw_arrow(line.start_anchor, line.end_anchor, position)
        elif cap_type == "tick":
            self._draw_tick(line, position)
        elif cap_type == "circle":
            self._draw_circle(line, position)
        else:
            print("Unknown cap type", cap_type)

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
