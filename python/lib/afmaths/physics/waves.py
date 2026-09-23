from afmaths.constants import SPEED_OF_LIGHT_METRES_PER_SECONDS
from afmaths.operation import divide_by


def wavelength(frequency_in_hertz: float) -> float:
    """Returns wavelength in metres"""
    return divide_by(frequency_in_hertz)(SPEED_OF_LIGHT_METRES_PER_SECONDS)


def frequency(wavelength_in_metres: float) -> float:
    """Returns frequency in hertz"""
    return divide_by(wavelength_in_metres)(SPEED_OF_LIGHT_METRES_PER_SECONDS)
