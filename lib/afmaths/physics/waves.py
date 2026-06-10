from afmaths.constants import SPEED_OF_LIGHT_METRES_PER_SECONDS
from afmaths.operation import divide_by


def frequency_to_wavelength(frequency_in_hertz: float) -> float:
    """Returns wavelength in metres"""
    return divide_by(frequency_in_hertz)(SPEED_OF_LIGHT_METRES_PER_SECONDS)


def wavelength_to_frequency(wavelength_in_metres: float) -> float:
    """Returns frequency in hertz"""
    return divide_by(wavelength_in_metres)(SPEED_OF_LIGHT_METRES_PER_SECONDS)
