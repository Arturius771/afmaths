from astronomy_types import (
    EquatorialCoordinates,
    OrbitalElements,
    Radians,
    Scalar,
)

from afmaths.afmath_types import Area
from afmaths.constants import STEFAN_BOLTZMANN_CONSTANT
from afmaths.operation import divide_by, exponentiate, multiply, subtract
from afmaths.physics.electromagnetism import stefan_boltzmann_law
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    angle_above_orbital_plane,
)


def beta_angle(sun: EquatorialCoordinates, orbit: OrbitalElements) -> Radians:
    """Calculates the beta angle, which is the angle between the Sun and the orbital plane of the satellite."""
    return angle_above_orbital_plane(sun, orbit)


def radiator_emission(
    emission_coefficient: float, area: Area, radiator_temp: float, ambient_temp: float
) -> float:
    """Calculates the thermal emission from a radiator based on its emission coefficient, area, radiator temperature, and ambient temperature."""
    return stefan_boltzmann_law(
        emission_coefficient, area, subtract(ambient_temp)(radiator_temp)
    )


def radiator_area(
    emission_coefficient: float, emitted_power: float, temperature: float
) -> Area:
    """Calculates the required radiator area based on its emission coefficient, emitted power, and temperature."""
    return Area(
        Scalar(
            divide_by(emitted_power)(
                multiply(STEFAN_BOLTZMANN_CONSTANT)(
                    multiply(emission_coefficient)(exponentiate(4)(temperature))
                )
            )
        )
    )


# endregion
