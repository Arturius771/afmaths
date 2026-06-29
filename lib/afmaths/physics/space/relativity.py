from afmaths.constants import (
    GRAVITATIONAL_CONSTANT,
    SPEED_OF_LIGHT_METRES_PER_SECONDS,
    Mass,
)
from afmaths.operation import DOUBLE, SQUARE, divide_by, multiply
from astronomy_types import Distance


def calculate_schwarzschild_radius(mass: Mass) -> Distance:
    """
    Calculates the size an object would have to be shrunk down to to become a black hole.

    :param mass: The mass of the object d
    :type mass: float
    :return: The radius in metres
    :rtype: float
    """
    return divide_by(SQUARE(SPEED_OF_LIGHT_METRES_PER_SECONDS))(
        multiply(DOUBLE(GRAVITATIONAL_CONSTANT))(mass)
    )
