from dataclasses import dataclass
import math
from afmaths.constants import (
    GRAVITATIONAL_CONSTANT,
    SPEED_OF_LIGHT_METRES_PER_SECONDS,
    Area,
    Force,
    Mass,
    Momentum,
)
from afmaths.operation import (
    DOUBLE,
    HALF,
    SQUARE,
    divide_by,
    multiply,
    ratio,
    subtract,
)
from astronomy_types import (
    Acceleration,
    Distance,
    Ratio,
    Scalar,
    Velocity,
)


def dynamic_pressure(fluid_mass_density: float, flow_speed: float) -> float:
    """Calculates the dynamic pressure of a fluid"""
    return multiply(HALF(fluid_mass_density))(SQUARE(flow_speed))


def watts_to_decibel_milliwatts(power_in_watts: float) -> float:
    """Converts watts to decibels relative to one milliwatt"""
    return decibels(power_in_watts)(0.001)


def decibels(power1: float):
    """Returns a function that calculates the decibels between two powers"""
    return lambda power2: math.log(power1 / power2, 10)


def momentum(mass: Mass, velocity: Velocity) -> Momentum:
    return multiply(mass)(velocity)


def force(mass: Mass, acceleration: Acceleration) -> Force:
    """Newton's second law"""
    return multiply(mass)(acceleration)


def pushing_to_resisting_force_ratio(
    pushing_force: Force, resisting_force: Force
) -> Ratio:
    return Ratio(Scalar(ratio(pushing_force)(resisting_force)))


def net_acceleration(
    pushing: Force,
    mass: Mass,
    constant_resistance: Acceleration = Acceleration(Scalar(0)),
) -> Acceleration:
    return subtract(constant_resistance)(divide_by(mass)(pushing))


def refractive_index(angle_of_incidence_1: float, angle_of_incedence_2: float):
    """Find the refractive index of a material by rearranging Snell's law and measuring the change of angle in and out of the material."""
    return divide_by(math.sin(angle_of_incedence_2))(math.sin(angle_of_incidence_1))


def diameter_of_distant_object(
    distance: float, angular_diameter_degrees: float
) -> float:
    """Returns the diameter of an object if the distance and angular diameter are known"""
    # Rearranges the equation in angular_diameter_degrees()
    return math.tan(math.radians(angular_diameter_degrees)) * distance


def centripetal_acceleration(velocity: Velocity, radius: Distance) -> Acceleration:
    # From MSE SFM Exercise 1
    # Equal to gravitational acceleration for circular orbits.
    return divide_by(radius)(SQUARE(velocity))


def centripetal_force(acceleration: Acceleration, mass: Mass) -> Force:
    return force(mass, acceleration)
