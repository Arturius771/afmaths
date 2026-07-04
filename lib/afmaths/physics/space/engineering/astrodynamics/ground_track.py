import math
from astronomy_types import (
    Radians,
    Scalar,
    Second,
    Inclination,
    Latitude,
    Degrees,
    MeanMotion,
)

from afmaths.operation import (
    divide_by,
    multiply,
    negate,
)


def max_latitude(i: Inclination) -> Latitude:
    return Degrees(Scalar(math.degrees(i)))


def min_latitude(i: Inclination) -> Latitude:
    return Degrees(Scalar(negate(math.degrees(i))))


def westward_drift(n: MeanMotion) -> Degrees:
    return Degrees(Scalar(multiply(360)(divide_by(n)(1))))


def westware_drift_from_angular_velocity_and_period(
    body_angular_velocity: Radians, orbital_period: Second
) -> Radians:
    return multiply(body_angular_velocity)(orbital_period)
