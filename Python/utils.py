from __future__ import annotations
import math
from typing import Optional
import rv.commands as crv


class Vector:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}> x: {self.x} y: {self.y}"

    @property
    def magnitude(self):
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
    def __init__(self, x, y) -> None:
        super().__init__(x, y)


class ScreenVector(Vector):
    def __init__(self, x, y) -> None:
        super().__init__(x, y)


class Point:
    def __init__(self, x, y, source: Optional[str] = None) -> None:
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

    def distance_to(self, end_point: Point) -> float:
        return math.sqrt(self.distance_to_squared(end_point))

    def distance_to_squared(self, end_point: Point) -> float:
        dx = end_point.x - self.x
        dy = end_point.y - self.y

        return dx**2 + dy**2

    def lerp(self, other: Point, t: float) -> Point:
        """Linear interpolation between the point and another point

        Parameters
        ----------
        other : Point
            The point we are interlpolating toward
        t : float
            Position along the line from self (0) to other (1).

        Returns
        -------
        Point
            New interpolated point between self and other

        """
        return self.__class__(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            source=self.source,
        )


class ImagePoint(Point):
    def __init__(self, x, y, source: Optional[str] = None) -> None:
        super().__init__(x, y, source)

    @property
    def screenspace(self):
        if self.source:
            return crv.imageToEventSpace(self.source, (self.x, self.y))

    @property
    def screen_x(self):
        return self.screenspace[0] if self.screenspace else None

    @property
    def screen_y(self):
        return self.screenspace[1] if self.screenspace else None

    def to_screenspace(self):
        return ScreenPoint(self.screen_x, self.screen_y, source=self.source)

    def direction_to(self, end_point: Point) -> Vector:
        return ImageVector(end_point.x - self.x, end_point.y - self.y)

    def invalidate(self):
        self._screenspace = None

    def move(self, dx, dy):
        self.x = self.x + dx
        self.y = self.y + dy
        self.invalidate()


class ScreenPoint(Point):
    def __init__(self, x, y, source: Optional[str] = None) -> None:
        super().__init__(x, y, source)

    @property
    def imagespace(self):
        if self.source:
            return crv.eventToImageSpace(self.source, (self.x, self.y))

    @property
    def image_x(self):
        return self.imagespace[0] if self.imagespace else None

    @property
    def image_y(self):
        return self.imagespace[1] if self.imagespace else None

    def to_imagespace(self) -> ImagePoint:
        return ImagePoint(self.image_x, self.image_y, source=self.source)

    def direction_to(self, end_point: Point) -> ScreenVector:
        return ScreenVector(end_point.x - self.x, end_point.y - self.y)
