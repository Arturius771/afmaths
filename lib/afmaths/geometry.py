from astronomy_types import (
    Coordinate2D,
    Distance,
    Eccentricity,
    Ratio,
    Scalar,
    SemiMajorAxis,
    SemiMinorAxis,
)

from .operation import (
    HALF,
    SQUARE,
    add,
    divide,
    exponentiate,
    multiply,
    subtract,
)
import math
from .formula import taylor_series

pythagoras = lambda a: lambda b: add(SQUARE(a))(SQUARE(b))


def euclid(m: int, n: int) -> int:
    """Given two positive integers, m and n, find their greatest common divisor which is the largest positive integer that divides both evenly."""

    remainder = m % n
    if remainder == 0:
        return n
    else:
        m = n
        n = remainder
        euclid(m, n)
    return n


def sieve_of_eratosthenes(n: int) -> list[int]:
    """Finds prime numbers up to n"""
    # https://www.youtube.com/watch?v=fwxjMKBMR7s
    numbers = [True] * n
    primes = []

    for index in range(2, n):
        if numbers[index]:
            primes.append(index)
            for multiple in range(index * index, n, index):
                numbers[multiple] = False

    return primes


def tangent(angle_degrees: float) -> float:
    """Returns a value in radians"""
    return divide(cosine(angle_degrees))(sine(angle_degrees))


def arctangent(radians):
    return math.degrees(math.atan(radians))


def sine(angle_degrees: float) -> float:
    """Returns a value in radians"""
    return taylor_series(math.radians(angle_degrees))(math.radians(angle_degrees), 2, 3)


def cosine(angle_degrees: float) -> float:
    """Returns a value in radians"""
    return taylor_series(math.radians(angle_degrees))(1, 2, 2)


# TODO: Check naming, this may be valid for more than just right triangles
def area_of_right_triangle(base_length: float, height_length: float) -> float:
    """Area = base * height / 2"""
    return HALF(multiply(base_length)(height_length))


def area_of_quarter_circle(side_length: float, radius: float) -> float:
    """Area = s^2 - ((1/4)*pi*r^2)"""
    return subtract((divide(4)(1)) * math.pi * SQUARE(radius))(SQUARE(side_length))


def semi_major_axis_from_axes(a: float, b: float) -> SemiMajorAxis:
    """Returns the semi major axis of an ellipse given the lengths of the two axes"""
    return HALF(add(a)(b))


def draw_circle_bounding_box(
    coordinates: Coordinate2D, radius: Distance
) -> tuple[Coordinate2D, Coordinate2D]:
    """
    Calculate the bounding box of a circle given its center coordinates and radius.

    Parameters:
    x (float): The x-coordinate of the circle's center.
    y (float): The y-coordinate of the circle's center.
    radius (float): The radius of the circle.

    Returns:
    tuple: A tuple containing the coordinates of the bounding box in the format (x0, y0, x1, y1).
    """
    return draw_ellipse(
        coordinates, SemiMajorAxis(radius), Eccentricity(Ratio(Scalar(0)))
    )


def draw_ellipse(
    coordinates: Coordinate2D, radius: SemiMajorAxis, eccentricity: Eccentricity
) -> tuple[Coordinate2D, Coordinate2D]:
    """
    Returns:
    tuple: A tuple containing the coordinates of the bounding box in the format (x0, y0, x1, y1).
    """
    if eccentricity < 0 or eccentricity >= 1:
        raise ValueError("Eccentricity must be in the range [0, 1).")

    semi_minor_axis = calculate_semi_minor_axis(SemiMajorAxis(radius), eccentricity)

    return (
        Coordinate2D(coordinates.x - radius, coordinates.y - semi_minor_axis),
        Coordinate2D(coordinates.x + radius, coordinates.y + semi_minor_axis),
    )


def calculate_semi_minor_axis(
    semi_major_axis: SemiMajorAxis, eccentricity: Eccentricity
) -> SemiMinorAxis:
    return exponentiate(0.5)(multiply(semi_major_axis)(1 - SQUARE(eccentricity)))


# def calculate_semi_minor_axis(
#     semi_major_axis: SemiMajorAxis, eccentricity: Eccentricity
# ) -> float:
#     """
#     Calculate the semi-minor axis of an ellipse given its semi-major axis and eccentricity.

#     Parameters:
#     a (float): The semi-major axis of the ellipse.
#     e (float): The eccentricity of the ellipse (0 <= eccentricity < 1).

#     Returns:
#     float: The semi-minor axis of the ellipse.
#     """
#     if eccentricity < 0 or eccentricity >= 1:
#         raise ValueError("Eccentricity must be in the range [0, 1).")

#     return semi_major_axis * (1 - eccentricity**2) ** 0.5


def calculate_distance(
    coordinates1: Coordinate2D, coordinates2: Coordinate2D
) -> Distance:
    """
    Calculate the distance between two points in 2D space.

    Parameters:
    x1 (float): The x-coordinate of the first point.
    y1 (float): The y-coordinate of the first point.
    x2 (float): The x-coordinate of the second point.
    y2 (float): The y-coordinate of the second point.

    Returns:
    float: The distance between the two points.
    """
    return (
        (coordinates2.x - coordinates1.x) ** 2 + (coordinates2.y - coordinates1.y) ** 2
    ) ** 0.5


def calculate_foci(
    semi_major_axis: SemiMajorAxis, eccentricity: Eccentricity
) -> tuple[Coordinate2D, Coordinate2D]:
    """
    Calculate the coordinates of the foci of an ellipse given its semi-major axis and eccentricity.

    Parameters:
    a (float): The semi-major axis of the ellipse.
    e (float): The eccentricity of the ellipse (0 <= eccentricity < 1).

    Returns:
    tuple: A tuple containing the coordinates of the two foci in the format ((x1, y1), (x2, y2)).
    """
    if eccentricity < 0 or eccentricity >= 1:
        raise ValueError("Eccentricity must be in the range [0, 1).")

    c = semi_major_axis * eccentricity
    # [X1, Y1] = (-c, 0) and [X2, Y2] = (c, 0) for an ellipse centered at the origin
    return (Coordinate2D(-c, 0), Coordinate2D(c, 0))


def calculate_semi_major_axis(
    radius: Distance, eccentricity: Eccentricity
) -> SemiMajorAxis:
    """
    Calculate the semi-major axis of an ellipse given the distance from the center to a point on the ellipse and the eccentricity.

    Parameters:
    r (float): The distance from the center of the ellipse to a point on the ellipse.
    e (float): The eccentricity of the ellipse (0 <= eccentricity < 1).

    Returns:
    float: The semi-major axis of the ellipse.
    """
    if eccentricity < 0 or eccentricity >= 1:
        raise ValueError("Eccentricity must be in the range [0, 1).")

    return SemiMajorAxis(Distance(Scalar(radius / (1 - eccentricity))))
