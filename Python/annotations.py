from __future__ import annotations
from collections import defaultdict
from typing import Optional
from OpenGL import GL
from PySide6 import QtGui
import rv.commands as crv
from utils import ImagePoint, ScreenPoint, RectEdges, SourceName, SourceNode, Color


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
    """A single annotation class"""

    editable_properties = ["width", "color", "opacity", "fill_color", "fill_opacity"]

    def __init__(
        self,
        start: ImagePoint,
        end: ImagePoint,
        source: SourceName,
        width: float = 1.0,
        color: tuple = (1, 0, 0, 1),
        opacity: float = 1.0,
        fill_color: tuple = (1, 1, 1, 1),
        fill_opacity: float = 1.0,
    ) -> None:
        """Create a stroke

        Parameters
        ----------
        start : ImagePoint
            Start point in image space
        end : ImagePoint
            Start point in image space
        source : SourceName
            The source the stroke is attached to. Note that this is the source name not the node
            since we need the actual source to calculate image/screen space
        width : float
            Stroke width
        color : tuple
            Storke color in normalized rgba values
        opacity : float
            Stroke opacity
        fill_color : tuple
            Storke fill color in normalized rgba values
        fill_opacity : float
            Stroke fill opacity

        """
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
