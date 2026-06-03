from afmaths.operation import divide
from afmaths.physics.physics import SPEED_OF_LIGHT_METRES_PER_SECONDS


def frequency_to_wavelength(frequency_in_hertz: float) -> float:
    """Returns wavelength in metres"""
    return divide(frequency_in_hertz)(SPEED_OF_LIGHT_METRES_PER_SECONDS)


def wavelength_to_frequency(wavelength_in_metres: float) -> float:
    """Returns frequency in hertz"""
    return divide(wavelength_in_metres)(SPEED_OF_LIGHT_METRES_PER_SECONDS)
