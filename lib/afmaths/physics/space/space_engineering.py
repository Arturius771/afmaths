from astronomy_types import (
    EquatorialCoordinates,
    OrbitalElements,
    Radians,
    Scalar,
)

from afmaths.constants import EXAMPLE_ELEMENTS
from afmaths.physics.space.astrodynamics import angle_above_orbital_plane


# region Thermal SUbsystem
def beta_angle(sun: EquatorialCoordinates, orbit: OrbitalElements) -> Radians:
    return angle_above_orbital_plane(sun, orbit)


# endregion

if __name__ == "__main__":
    print(
        beta_angle(
            EquatorialCoordinates(Radians(Scalar(12)), Radians(Scalar(12))),
            EXAMPLE_ELEMENTS,
        )
    )
