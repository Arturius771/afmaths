from astronomy_types import (
    EquatorialCoordinates,
    OrbitalElements,
    Radians,
    Scalar,
)

from afmaths.constants import EXAMPLE_ELEMENTS, STEFAN_BOLTZMANN_CONSTANT
from afmaths.operation import divide_by, exponentiate, multiply, subtract
from afmaths.physics.electromagnetism import stefan_boltzmann_law
from afmaths.physics.space.engineering.astrodynamics.maneuvers import (
    angle_above_orbital_plane,
)
from afmaths.types import Area


def beta_angle(sun: EquatorialCoordinates, orbit: OrbitalElements) -> Radians:
    return angle_above_orbital_plane(sun, orbit)


def radiator_emission(
    emission_coefficient: float, area: Area, radiator_temp: float, ambient_temp: float
) -> float:
    return stefan_boltzmann_law(
        emission_coefficient, area, subtract(ambient_temp)(radiator_temp)
    )


def radiator_area(
    emission_coefficient: float, emitted_power: float, temperature: float
) -> Area:
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

if __name__ == "__main__":
    print(
        beta_angle(
            EquatorialCoordinates(Radians(Scalar(12)), Radians(Scalar(12))),
            EXAMPLE_ELEMENTS,
        )
    )
