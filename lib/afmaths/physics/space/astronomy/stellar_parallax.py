import math

from astronomy_types import Degrees, Radians, Distance, Scalar
from afmaths.constants import ASTRONOMICAL_UNIT
from afmaths.operation import HALF, divide_by
from afmaths.physics.space.astronomy.utils import (
    metres_from_astronomical_unit,
)


def distance_from_stellar_parallax(
    angle: Degrees, radius: Distance = ASTRONOMICAL_UNIT
) -> Distance:
    """Calculate stellar distance from the parallax angle θ."""
    return Distance(Scalar(divide_by(math.tan(math.radians(angle)))(radius)))


def distance_from_stellar_parallax_full_angular_displacement(
    angle: Degrees, radius: Distance = ASTRONOMICAL_UNIT
) -> Distance:
    """Calculate stellar distance from the total parallax angle θ."""
    return Distance(Scalar(divide_by(math.tan(HALF(math.radians(angle))))(radius)))
