from afmaths.constants import PLANCK_CONSTANT, STEFAN_BOLTZMANN_CONSTANT
from afmaths.operation import SQUARE, divide_by, exponentiate, multiply
from afmaths.physics.physics import inverse_square_law
from afmaths.types import Area


def flux_density(luminosity: float, distance_metres: float) -> float:
    """Calculates the flux density of a light source"""
    return inverse_square_law(luminosity, distance_metres)


def radiowave_relative_power_distances(distance1: float, distance2: float) -> tuple:
    """Calculates the relative power distances of two radio waves"""
    ##TM255 Block 1
    distance_ratio = divide_by(distance1)(distance2)
    quartic = exponentiate(4)
    distance1_strength = quartic(distance_ratio)
    divide_by_distance_1_strength = divide_by(distance1_strength)
    distance2_strength = divide_by_distance_1_strength(1)

    return distance_ratio, distance1_strength, distance2_strength


def radiowave_received_power_difference_by_distance(
    power_in_watts_at_distance1: float, distance1: float, distance2: float
) -> float:
    """Calculates the difference in received power between two distances"""
    # https://www.youtube.com/watch?v=BF73QaY1aEg
    cross_multiply = multiply(power_in_watts_at_distance1)(SQUARE(distance1))
    return divide_by(SQUARE(distance2))(cross_multiply)


def photon_energy_from_wavelength(wavelength_in_micrometer: float) -> float:
    """Returns photon energy in electrovolts"""
    return divide_by(wavelength_in_micrometer)(1.2398)


def photon_energy_from_frequency(frequency_in_hertz: float) -> float:
    """Returns photon energy in joules"""
    return multiply(PLANCK_CONSTANT)(frequency_in_hertz)


def stefan_boltzmann_law(
    emission_coefficient: float, surface_area: Area, temperature: float
) -> float:
    """Returns the amount of power radiated in Watts by a black body."""
    return multiply(STEFAN_BOLTZMANN_CONSTANT)(
        multiply(emission_coefficient)(
            multiply(surface_area)(exponentiate(4)(temperature))
        )
    )
