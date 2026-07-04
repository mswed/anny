from __future__ import annotations
import math
from typing import Optional, NamedTuple, NewType, Self
import rv.commands as crv


class Vector:
    """Base class for vector math

    Attributes
    ----------
    x : x coordinate
    y : y coordinate

    """

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}> x: {self.x} y: {self.y}"

    @property
    def magnitude(self) -> Optional[float]:
        # Magnitude
        m = math.sqrt(self.x**2 + self.y**2)
        if m == 0:
            # line length is 0
            return

        return m

    @property
    def normalized(self):
        if self.magnitude:
            return self.__class__(self.x / self.magnitude, self.y / self.magnitude)

    @property
    def perpendicular(self):
        return self.__class__(-self.y, self.x)

    def __mul__(self, scalar: float):
        return self.__class__(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float):
        return self.__mul__(scalar)

    def __add__(self, other: Vector):
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector):
        return self.__class__(self.x - other.x, self.y - other.y)

    def __iter__(self):
        yield self.x
        yield self.y


class ImageVector(Vector):
    """Vector in image space"""

    def __init__(self, x, y) -> None:
        super().__init__(x, y)


class ScreenVector(Vector):
    """Vector in screen space"""

    def __init__(self, x, y) -> None:
        super().__init__(x, y)


class Point:
    """Base class for 2D point

    Attributes
    ----------
    x : x coordinate
    y : y coordinate
    source : RV source name (includes frame number) for converstion between image and screen space

    """

    def __init__(self, x: float, y: float, source: Optional[Source] = None) -> None:
        self.x = x
        self.y = y
        self.source = source

    def __add__(self, vector: Vector):
        return self.__class__(self.x + vector.x, self.y + vector.y, source=self.source)

    def __sub__(self, vector: Vector):
        return self.__class__(self.x - vector.x, self.y - vector.y, source=self.source)

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}> x: {self.x} y: {self.y}"

    def distance_to(self, target: Point) -> float:
        """Distance between the current point and the target point

        Parameters
        ----------
        target : Point
            Point to measure the distance to

        Returns
        -------
        float
            Distance between the two points

        """
        return math.sqrt(self.distance_to_squared(target))

    def distance_to_squared(self, target: Point) -> float:
        """Distace squared between the current point and the target. Can be used on its own
        to avoid the mildly expencive root operation

        Parameters
        ----------
        target : Point
            Point to measure the distance to

        Returns
        -------
        float
            Squared distance between the two points

        """
        dx = target.x - self.x
        dy = target.y - self.y

        return dx**2 + dy**2

    def lerp(self, target: Self, t: float) -> Self:
        """Linear interpolation between the point and another point

        Parameters
        ----------
        target : Self
            The point we are interlpolating toward
        t : float
            Position along the line from self (0) to other (1).

        Returns
        -------
        Self
            New interpolated point between self and other

        """
        return self.__class__(
            self.x + (target.x - self.x) * t,
            self.y + (target.y - self.y) * t,
            source=self.source,
        )


class ImagePoint(Point):
    """Point in image space

    Attributes
    ----------
    x : x coordinate
    y : y coordinate
    source : RV source name (includes frame number) for converstion between image and screen space

    """

    def __init__(self, x: float, y: float, source: Optional[Source] = None) -> None:
        super().__init__(x, y, source)

    @property
    def screenspace(self) -> Optional[tuple]:
        """The point coordinates in screen space

        Returns
        -------
        tuple
            x, y coordinates of point in screen space if we are able to convert to screen space. None otherwise

        """
        if self.source:
            return crv.imageToEventSpace(self.source.name, (self.x, self.y))

    @property
    def screen_x(self) -> Optional[float]:
        """Point x in screen space times the device pixel aspect so ratina displays also work

        Returns
        -------
        Optional[float]
            x coordinate of point in screen space if we are able to convert to screen space. None otherwise

        """
        ratio = crv.devicePixelRatio() or 1.0
        return self.screenspace[0] * ratio if self.screenspace else None

    @property
    def screen_y(self) -> Optional[float]:
        """Point y in screen space times the device pixel aspect so ratina displays also work

        Returns
        -------
        Optional[float]
            y coordinate of point in screen space if we are able to convert to screen space. None otherwise

        """
        ratio = crv.devicePixelRatio() or 1.0
        return self.screenspace[1] * ratio if self.screenspace else None

    def to_screenspace(self) -> Optional[ScreenPoint]:
        """Convert the point to an screen space point

        Returns
        -------
        ScreenPoint
            The point in screen space if we are able to calcualte. None otherwise

        """
        if self.screen_x is not None and self.screen_y is not None:
            return ScreenPoint(self.screen_x, self.screen_y, source=self.source)

    def direction_to(self, target: Point) -> ImageVector:
        """Direction vector between the current point and a target point

        Parameters
        ----------
        target : Point
            Point to calculate direction to

        Returns
        -------
        ImageVector
            Direction as an image vector

        """
        return ImageVector(target.x - self.x, target.y - self.y)

    def move(self, dx: float, dy: float) -> None:
        """Move the point to new coordinates (we only move points in image space)

        Parameters
        ----------
        dx : float
            X delta between current point and new position
        dy : float
            Y delta between current point and new position
        """
        self.x = self.x + dx
        self.y = self.y + dy


class ScreenPoint(Point):
    """Point in screen space

    Attributes
    ----------
    x : x coordinate
    y : y coordinate
    source : RV source name (includes frame number) for converstion between image and screen space

    """

    def __init__(self, x: float, y: float, source: Optional[Source] = None) -> None:
        super().__init__(x, y, source)

    @property
    def imagespace(self):
        """The point coordinates in image space

        Returns
        -------
        tuple
            x, y coordinates of point in image space if we are able to convert to screen space. None otherwise

        """
        if self.source:
            return crv.eventToImageSpace(self.source.name, (self.x, self.y))

    @property
    def image_x(self):
        """Point x in screen space

        Returns
        -------
        Optional[float]
            x coordinate of point in screen space if we are able to convert to screen space. None otherwise

        """
        return self.imagespace[0] if self.imagespace else None

    @property
    def image_y(self):
        """Point y in screen space

        Returns
        -------
        Optional[float]
            y coordinate of point in screen space if we are able to convert to screen space. None otherwise

        """
        return self.imagespace[1] if self.imagespace else None

    def to_imagespace(self) -> Optional[ImagePoint]:
        """Convert the point to an image space point

        Returns
        -------
        ImagePoint
            The point in image space if we are able to calculate. None otherwise

        """
        if self.image_x and self.image_y:
            return ImagePoint(self.image_x, self.image_y, source=self.source)

    def direction_to(self, target: Point) -> ScreenVector:
        """Direction vector between the current point and a target point

        Parameters
        ----------
        target : Point
            Point to calculate direction to

        Returns
        -------
        ScreenVector
            Direction as a screen vector

        """
        return ScreenVector(target.x - self.x, target.y - self.y)


class RectEdges(NamedTuple):
    """A class to store x axis aligned rectangle edges. Top should always be the hightest Y
    all values are stored and returned in screen space

    Attributes
    ----------
    left : X coordinate of the left edge
    right : X coordinate of the right edge
    top : Y coordinate of the top edge
    bottom : Y coordinate of the bottom edge
    """

    left: float
    right: float
    top: float
    bottom: float

    @property
    def bottom_left(self) -> ScreenPoint:
        return ScreenPoint(self.left, self.bottom)

    @property
    def bottom_right(self) -> ScreenPoint:
        return ScreenPoint(self.right, self.bottom)

    @property
    def top_right(self) -> ScreenPoint:
        return ScreenPoint(self.right, self.top)

    @property
    def top_left(self) -> ScreenPoint:
        return ScreenPoint(self.left, self.top)

    @property
    def width(self) -> float:
        """The rectangle width

        Returns
        -------
        float
            The width of the rectangle

        """
        return abs(self.right - self.left)

    @property
    def height(self) -> float:
        """The rectangle height

        Returns
        -------
        float
            The height of the rectangle

        """
        return abs(self.top - self.bottom)

    @property
    def corners(self) -> tuple:
        """The rectangle corners (used for OpenGL rendering)

        Returns
        -------
        tuple
            The rectangle corners in screen space

        """
        return (self.bottom_left, self.bottom_right, self.top_right, self.top_left)

    def padded(self, padding: int) -> RectEdges:
        """Convert the rectangle to a padded rectangle

        Parameters
        ----------
        padding : int
            The amount of padding to add to the rectangle

        Returns
        -------
        RectEdges
            The new rectangle with padding

        """
        return RectEdges(
            self.left - padding,
            self.right + padding,
            self.top + padding,
            self.bottom - padding,
        )

    def inset(self, margin) -> RectEdges:
        """Convert the rectangle to an inset rectangle (margin instead of padding)

        Parameters
        ----------
        margin : int
            The amount of margine to remove from the rectangle

        Returns
        -------
        RectEdges
            The new smaller rectangle

        """
        return RectEdges(
            self.left + margin,
            self.right - margin,
            self.top - margin,
            self.bottom + margin,
        )


class QuadCorners(NamedTuple):
    """
    Store a quad's corner vertex. Used to store mainly rotated rects. Stores all values in
    screen space

    Attributes
    ----------
    bottom_left : bottom left corner of the rectangle
    bottom_right : bottom left corner of the rectangle
    top_right : top right corner of the rectangle
    top_left : top left corner of the rectangle

    """

    bottom_left: ScreenPoint
    bottom_right: ScreenPoint
    top_right: ScreenPoint
    top_left: ScreenPoint


class ArrowVerts(NamedTuple):
    """Store an arrows verts. Stores all values in screen space

    Attributes
    ----------
    tip : The tip of the arrrow
    left_wing : The left wing of the arrow
    right_wing : The right wing of the arrow
    base : The base of the arrow
    line_base : The position where the line meets the arrow

    """

    tip: ScreenPoint
    left_wing: ScreenPoint
    right_wing: ScreenPoint
    base: ScreenPoint
    line_base: ScreenPoint


class LineVerts(NamedTuple):
    """Store a line's vertex. A line in this case is actually a (thin) rectangle, so we store
    all the points a rectangle would have along with some additional ones that are specific to what
    the line can do.

    Attributes
    ----------
    bottom_left : Bottom left corner of line's body
    bottom_right : Bottom right corner of line's body
    top_right : Top right corner of line's body
    top_left : Top left forner of line's body
    mid_left : The middle point of the left edge (the start of the line)
    mid_right : The middle point of the right edge (the end of the line)
    start_anchor : The original start point of the line as drawn by the user (used to draw handles and move the point)
    end_anchor : The original end point of the line as drawn by the user (used to draw handles and move the point)
    midpoint : The midpoint of the line (used to draw text)
    start_arrow : The calculate start arrow verts (if needed)
    end_arrow : The calculated end arrow verts (of needed)
    perp : The perpendicular direction vector of the line (used for ticks and arrow calc)
    half_offset : The perp * half the line width for handle calculations

    """

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
    """Store verts for line tick (end or start of line). All values are stored as
    screen points

    Attributes
    ----------
    top : Top point of the tick
    bottom : Bottom point of the tick

    """

    top: ScreenPoint
    bottom: ScreenPoint


class Color(NamedTuple):
    """Store color as rgba in a tuple

    Attributes
    ----------
    r : red
    g : green
    b : blue
    a : alpha

    """

    r: float
    g: float
    b: float
    a: float


class Source(NamedTuple):
    name: str
    node: str


SourceName = NewType("SourceName", str)
SourceNode = NewType("SourceNode", str)
