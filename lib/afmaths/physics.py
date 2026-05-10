import math
from formula import inverse_square_law
from geometry import area_of_right_triangle
from graph import GraphCoordinates, slope_gradiant
from operation import (
    HALF,
    SQUARE,
    add,
    divide,
    exponentiate,
    multiply,
    subtract,
)
from astronomy_types import Scalar, Distance

SPEED_OF_LIGHT_METRES_PER_SECONDS = 299792458
PLANCK_CONSTANT = multiply(6.62607004)(exponentiate(-34)(10))
GRAVITATIONAL_CONSTANT = multiply(6.67430)(exponentiate(-11)(10))  # 6.67430e-11


### PHYSICS FORMULAS
def radiowave_relative_power_distances(distance1: float, distance2: float) -> tuple:
    """Calculates the relative power distances of two radio waves"""
    ##TM255 Block 1
    distance_ratio = divide(distance1)(distance2)
    quartic = exponentiate(4)
    distance1_strength = quartic(distance_ratio)
    divide_by_distance_1_strength = divide(distance1_strength)
    distance2_strength = divide_by_distance_1_strength(1)

    return distance_ratio, distance1_strength, distance2_strength


def radiowave_received_power_difference_by_distance(
    power_in_watts_at_distance1: float, distance1: float, distance2: float
) -> float:
    """Calculates the difference in received power between two distances"""
    # https://www.youtube.com/watch?v=BF73QaY1aEg
    cross_multiply = multiply(power_in_watts_at_distance1)(SQUARE(distance1))
    return divide(SQUARE(distance2))(cross_multiply)


def photon_energy_from_wavelength(wavelength_in_micrometer: float) -> float:
    """Returns photon energy in electrovolts"""
    divide_by_wavelength = divide(wavelength_in_micrometer)
    return divide_by_wavelength(1.2398)


def photon_energy_from_frequency(frequency_in_hertz: float) -> float:
    """Returns photon energy in joules"""
    return multiply(PLANCK_CONSTANT)(frequency_in_hertz)


def frequency_to_wavelength(frequency_in_hertz: float) -> float:
    """Returns wavelength in metres"""
    return divide(frequency_in_hertz)(SPEED_OF_LIGHT_METRES_PER_SECONDS)


def wavelength_to_frequency(wavelength_in_metres: float) -> float:
    """Returns frequency in hertz"""
    return divide(wavelength_in_metres)(SPEED_OF_LIGHT_METRES_PER_SECONDS)


def dynamic_pressure(fluid_mass_density: float, flow_speed: float) -> float:
    """Calculates the dynamic pressure of a fluid"""
    return multiply(HALF(fluid_mass_density))(SQUARE(flow_speed))


def watts_to_decibel_milliwatts(power_in_watts: float) -> float:
    """Converts watts to decibels relative to one milliwatt"""
    return decibels(power_in_watts)(0.001)


def decibels(power1: float):
    """Returns a function that calculates the decibels between two powers"""
    return lambda power2: math.log(power1 / power2, 10)


def flux_density(luminosity: float, distance_metres: float) -> float:
    """Calculates the flux density of a light source"""
    return inverse_square_law(luminosity, distance_metres)


def univesal_gravitation(
    mass1: Scalar, mass2: Scalar, distance_metres: Distance
) -> float:
    """
    Calculate the strength of the gravitational "force" between two objects.

    :param mass1: The first object's mass
    :type mass1: float
    :param mass2: The second object's mass
    :type mass2: float
    :param distance_metres: The distance between the two objects
    :type distance_metres: float
    :return: Description
    :rtype: float
    """
    return multiply(GRAVITATIONAL_CONSTANT)(
        multiply(mass1)(mass2) / SQUARE(distance_metres)
    )


def angular_diameter_degrees(distance: float, diameter: float) -> float:
    """Calculates the angular diameter of an object in degrees"""
    return math.degrees(diameter / distance)


def diameter_of_distant_object(
    distance: float, angular_diameter_degrees: float
) -> float:
    """Returns the diameter of an object if the distance and angular diameter are known"""
    # Rearranges the equation in angular_diameter_degrees()
    return math.tan(math.radians(angular_diameter_degrees)) * distance


def calculate_gravitional_parameter(mass1: float, mass2: float) -> float:
    """
    Calculates the graviational parameter (Mu) of two objects in m^3/s^2

    :param mass1: The first bodies mass
    :type mass1: float
    :param mass2: The second bodies mass
    :type mass2: float
    :return: Mu = G * (mass1 + mass2)
    :rtype: float
    """
    return multiply(GRAVITATIONAL_CONSTANT)(mass1 + mass2)


def calculate_schwarzschild_radius(mass: float) -> float:
    """
    Calculates the size an object would have to be shrunk down to to become a black hole.

    :param mass: The mass of the object d
    :type mass: float
    :return: The radius in metres
    :rtype: float
    """
    return divide(SQUARE(SPEED_OF_LIGHT_METRES_PER_SECONDS))(
        multiply(multiply(2)(GRAVITATIONAL_CONSTANT))(mass)
    )


def displacement_from_velocity_curve(
    slope_component_start: GraphCoordinates,
    slope_component_end: GraphCoordinates,
    slope_component_peak: GraphCoordinates,
    flat_component_start: GraphCoordinates = GraphCoordinates(0, 0),
    flat_component_end: GraphCoordinates = GraphCoordinates(0, 0),
) -> float:
    """Assumes a straight line slope."""
    # Credit: https://www.khanacademy.org/science/ap-college-physics-1/xf557a762645cccc5:kinematics/xf557a762645cccc5:visual-models-of-motion/a/what-are-velocity-vs-time-graphs

    slope_speed = area_of_right_triangle(
        slope_component_end.x - slope_component_start.x, slope_component_peak.y
    )

    return add(
        multiply(flat_component_start.y)(flat_component_end.x - flat_component_start.x)
    )(slope_speed)


def displacement_of_velocity_curve_section(
    complete_curve_start: GraphCoordinates,
    complete_curve_end: GraphCoordinates,
    complete_curve_peak: GraphCoordinates,
    first_slice_start: GraphCoordinates,
    first_slice_end: GraphCoordinates,
    first_slice_peak: GraphCoordinates,
    second_slice_start: GraphCoordinates,
    second_slice_end: GraphCoordinates,
    second_slice_peak: GraphCoordinates,
) -> float:
    """Calculate a sectional area under a triangular curve of a velocity over time graph."""
    return subtract(
        (
            add(
                displacement_from_velocity_curve(
                    first_slice_start,
                    first_slice_end,
                    first_slice_peak,
                )
            )(
                displacement_from_velocity_curve(
                    second_slice_start,
                    second_slice_end,
                    second_slice_peak,
                )
            )
        )
    )(
        displacement_from_velocity_curve(
            complete_curve_start,
            complete_curve_end,
            complete_curve_peak,
        )
    )


def average_acceleration_from_slope(
    time_and_velocity1: GraphCoordinates, time_and_velocity2: GraphCoordinates
) -> float:
    return slope_gradiant(time_and_velocity1, time_and_velocity2)


if __name__ == "__main__":
    print(
        displacement_from_velocity_curve(
            GraphCoordinates(3, 6),
            GraphCoordinates(7, 0),
            GraphCoordinates(5, 6),
            GraphCoordinates(0, 6),
            GraphCoordinates(3, 6),
        )
    )  # 30
    print(
        average_acceleration_from_slope(GraphCoordinates(0, 3), GraphCoordinates(6, 0))
    )  # -0.5
    print(
        displacement_from_velocity_curve(
            GraphCoordinates(2, 0),
            GraphCoordinates(3, -5),
            GraphCoordinates(2.5, -5),
        )
    )  # -2.5
    print(
        displacement_from_velocity_curve(
            GraphCoordinates(0, 0),
            GraphCoordinates(2, 0),
            GraphCoordinates(1, 5),
        )
        + displacement_from_velocity_curve(
            GraphCoordinates(2, 0),
            GraphCoordinates(3, -5),
            GraphCoordinates(3, -5),
        )
    )  # 2.5

    print(
        displacement_of_velocity_curve_section(
            GraphCoordinates(0, 0),
            GraphCoordinates(2, 0),
            GraphCoordinates(1, 5),
            GraphCoordinates(0, 0),
            GraphCoordinates(0.5, 2.5),
            GraphCoordinates(0.5, 2.5),
            GraphCoordinates(1.5, 2.5),
            GraphCoordinates(2, 0),
            GraphCoordinates(1.5, 2.5),
        )
    )  # 3.75

    print(
        displacement_from_velocity_curve(
            GraphCoordinates(1, 0),
            GraphCoordinates(3, 4),
            GraphCoordinates(3, 4),
            GraphCoordinates(3, 4),
            GraphCoordinates(4, 4),
        )
    )  # 8

    print(
        displacement_from_velocity_curve(
            GraphCoordinates(1, 5),
            GraphCoordinates(2, 9),
            GraphCoordinates(1, 5),
        )
    )  # 2.5
