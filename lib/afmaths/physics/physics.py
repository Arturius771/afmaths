from dataclasses import dataclass
import math
from afmaths.operation import (
    HALF,
    SQUARE,
    divide,
    exponentiate,
    multiply,
)
from astronomy_types import (
    Acceleration,
    Coordinate2D,
    Scalar,
    Second,
    Vector2D,
    Velocity,
)

from afmaths.physics.kinematics import (
    detect_collision,
    propagate_vector,
    velocity_after_duration,
    velocity_time_average_acceleration_from_slope,
    velocity_time_curve_displacement,
    velocity_time_displacement_curve_section,
    velocity_time_displacement_flat,
)


@dataclass(frozen=True)
class TriangleDescription:
    start: Coordinate2D
    peak: Coordinate2D
    end: Coordinate2D


SPEED_OF_LIGHT_METRES_PER_SECONDS = 299792458
PLANCK_CONSTANT = multiply(6.62607004)(exponentiate(-34)(10))
GRAVITATIONAL_CONSTANT = multiply(6.67430)(exponentiate(-11)(10))  # 6.67430e-11


def dynamic_pressure(fluid_mass_density: float, flow_speed: float) -> float:
    """Calculates the dynamic pressure of a fluid"""
    return multiply(HALF(fluid_mass_density))(SQUARE(flow_speed))


def watts_to_decibel_milliwatts(power_in_watts: float) -> float:
    """Converts watts to decibels relative to one milliwatt"""
    return decibels(power_in_watts)(0.001)


def decibels(power1: float):
    """Returns a function that calculates the decibels between two powers"""
    return lambda power2: math.log(power1 / power2, 10)


def refractive_index(angle_of_incidence_1: float, angle_of_incedence_2: float):
    """Find the refractive index of a material by rearranging Snell's law and measuring the change of angle in and out of the material."""
    return divide(math.sin(angle_of_incedence_2))(math.sin(angle_of_incidence_1))


def diameter_of_distant_object(
    distance: float, angular_diameter_degrees: float
) -> float:
    """Returns the diameter of an object if the distance and angular diameter are known"""
    # Rearranges the equation in angular_diameter_degrees()
    return math.tan(math.radians(angular_diameter_degrees)) * distance


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


if __name__ == "__main__":
    print(
        velocity_time_displacement_curve_section(
            Coordinate2D(3, 6),
            Coordinate2D(7, 0),
        )
        + velocity_time_displacement_flat(
            Coordinate2D(0, 6),
            Coordinate2D(3, 6),
        )
    )  # 30
    print(
        velocity_time_average_acceleration_from_slope(
            Coordinate2D(0, 3), Coordinate2D(6, 0)
        )
    )  # -0.5
    print(
        velocity_time_displacement_curve_section(
            Coordinate2D(2, 0),
            Coordinate2D(3, -5),
        )
    )  # -2.5
    print(
        velocity_time_displacement_curve_section(
            Coordinate2D(0, 0),
            Coordinate2D(2, 0),
        )
        + velocity_time_displacement_curve_section(
            Coordinate2D(2, 0),
            Coordinate2D(3, -5),
        )
    )  # -2.5

    print(
        velocity_time_curve_displacement(
            [
                Coordinate2D(1, 5),
                Coordinate2D(0.5, 2.5),
                Coordinate2D(1.5, 2.5),
            ]
        )
    )  # 3.75

    print(
        velocity_time_displacement_curve_section(
            Coordinate2D(1, 0),
            Coordinate2D(3, 4),
        )
        + velocity_time_displacement_flat(
            Coordinate2D(3, 4),
            Coordinate2D(4, 4),
        )
    )  # 8

    print(
        velocity_time_displacement_curve_section(
            Coordinate2D(1, 5),
            Coordinate2D(2, 9),
        )
    )  # 2.5

    print(
        velocity_after_duration(
            Acceleration(Scalar(1)), Velocity(Scalar(0)), Second(Scalar(5))
        )
    )

    print(propagate_vector(Coordinate2D(0, 0), Vector2D(1, 1), 2))

    print(
        detect_collision(
            Coordinate2D(0, 0), Coordinate2D(2, 0), Vector2D(1, 0), Vector2D(-1, 0)
        )
    )
