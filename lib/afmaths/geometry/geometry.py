from astronomy_types import (
    Coordinate2D,
    Distance,
    Eccentricity,
    Ratio,
    Scalar,
    SemiLatusRectum,
    SemiMajorAxis,
    SemiMinorAxis,
)
from afmaths.constants import Area
from afmaths.formula import taylor_series
from afmaths.operation import (
    HALF,
    SQUARE,
    add,
    divide_by,
    multiply,
    square_root,
    subtract,
)
import math

pythagoras = lambda a: lambda b: add(SQUARE(a))(SQUARE(b))


def euclid(m: int, n: int) -> int:
    """Given two positive integers, m and n, find their greatest common divisor which is the largest positive integer that divides both evenly."""
    remainder = m % n
    if remainder == 0:
        return n
    return euclid(n, remainder)


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
    return divide_by(cosine(angle_degrees))(sine(angle_degrees))


def arctangent(radians):
    return math.degrees(math.atan(radians))


def sine(angle_degrees: float) -> float:
    """Returns a value in radians"""
    return taylor_series(math.radians(angle_degrees))(math.radians(angle_degrees), 2, 3)


def cosine(angle_degrees: float) -> float:
    """Returns a value in radians"""
    return taylor_series(math.radians(angle_degrees))(1, 2, 2)


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


def geometric_mean_distance(x: Distance, y: Distance) -> Distance:
    return Distance(Scalar(square_root(multiply(x)(y))))


# region Ellipses


def semi_minor_axis_from_semi_latus_rectum(
    semi_latus_rectum: SemiLatusRectum,
    semi_major_axis: SemiMajorAxis,
) -> SemiMinorAxis:
    return SemiMinorAxis(geometric_mean_distance(semi_latus_rectum, semi_major_axis))


def semi_minor_axis_from_vertex_distances(
    nearest_vertex_distance: Distance,
    farthest_vertex_distance: Distance,
) -> SemiMinorAxis:
    return SemiMinorAxis(
        geometric_mean_distance(nearest_vertex_distance, farthest_vertex_distance)
    )


def eccentricity_factor_minus(e: Eccentricity) -> Scalar:
    """1 - e"""
    return subtract(e)(1)  # 1 - e


def eccentricity_factor_plus(e: Eccentricity) -> Scalar:
    """1 + e"""
    return add(e)(1)  # 1 + e


def calculate_foci(
    a: SemiMajorAxis, e: Eccentricity
) -> tuple[Coordinate2D, Coordinate2D]:
    """
    Calculate the coordinates of the foci of an ellipse given its semi-major axis and eccentricity.

    Parameters:
    a (float): The semi-major axis of the ellipse.
    e (float): The eccentricity of the ellipse (0 <= eccentricity < 1).

    Returns:
    tuple: A tuple containing the coordinates of the two foci in the format ((x1, y1), (x2, y2)).
    """
    if e < 0 or e >= 1:
        raise ValueError("Eccentricity must be in the range [0, 1).")

    c = a * e
    # [X1, Y1] = (-c, 0) and [X2, Y2] = (c, 0) for an ellipse centered at the origin
    return (Coordinate2D(-c, 0), Coordinate2D(c, 0))


def semi_major_axis_from_nearest_vertex_distance(
    nearest_vertex_distance: Distance,
    e: Eccentricity,
) -> SemiMajorAxis:
    """
    Calculate the semi-major axis of an ellipse given the distance from the center to a point on the ellipse and the eccentricity.

    Parameters:
    r (float): The distance from the center of the ellipse to a point on the ellipse.
    e (float): The eccentricity of the ellipse (0 <= eccentricity < 1).

    Returns:
    float: The semi-major axis of the ellipse.
    """
    return SemiMajorAxis(
        Distance(Scalar(nearest_vertex_distance / (eccentricity_factor_minus(e))))
    )


def semi_major_axis_hyperbola(l: SemiLatusRectum, e: Eccentricity) -> SemiMajorAxis:
    if e <= 1:
        raise ValueError("Hyperbola eccentricity must be > 1.")
    return divide_by(subtract(1)(SQUARE(e)))(l)


def eccentricity(a: SemiMajorAxis, b: SemiMinorAxis) -> Eccentricity:
    return Eccentricity(
        Ratio(Scalar(square_root(subtract(divide_by(SQUARE(a))(SQUARE(b)))(1))))
    )


def semi_minor_axis(a: SemiMajorAxis, e: Eccentricity) -> SemiMinorAxis:
    # a * sqrt(1 - e**2)
    return multiply(a)(square_root(eccentricity_factor_minus(SQUARE(e))))


def semi_major_axis_from_vertex_distances(
    min_vertex_distance: Distance,
    max_vertex_distance: Distance,
) -> SemiMajorAxis:
    """Returns the semi major axis of an ellipse given the lengths of the two axes"""
    return SemiMajorAxis(HALF(add(min_vertex_distance)(max_vertex_distance)))


def circle_bounding_box(
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
    return ellipse_bounding_box(
        coordinates, SemiMajorAxis(radius), Eccentricity(Ratio(Scalar(0)))
    )


def ellipse_bounding_box(
    coordinates: Coordinate2D, a: SemiMajorAxis, e: Eccentricity
) -> tuple[Coordinate2D, Coordinate2D]:
    """
    Returns:
    tuple: A tuple containing the coordinates of the bounding box in the format (x0, y0, x1, y1).
    """
    if e < 0 or e >= 1:
        raise ValueError("Eccentricity must be in the range [0, 1).")

    b = semi_minor_axis(a, e)

    return (
        Coordinate2D(coordinates.x - a, coordinates.y - b),
        Coordinate2D(coordinates.x + a, coordinates.y + b),
    )


# endregion


# region Areas
def area(length: float, height: float) -> Area:
    return multiply(length)(height)


# TODO: Check naming, this may be valid for more than just right triangles
def area_of_right_triangle(base_length: float, height_length: float) -> Area:
    """Area = base * height / 2"""
    return HALF(multiply(base_length)(height_length))


def area_of_quarter_circle(side_length: float, radius: float) -> Area:
    """Area = s^2 - ((1/4)*pi*r^2)"""
    return subtract((divide_by(4)(1)) * math.pi * SQUARE(radius))(SQUARE(side_length))


# endregion
