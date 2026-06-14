import math

from afmaths.constants import EARTH_MU_KM_CUBED
from afmaths.physics.space.celestial_mechanics import orbit_radius
from afmaths.visualisations.helpers import (
    OrbitPlot2DSettings,
    TransferApsis,
    build_hohmann_transfer_2d_perifocal_figure,
)
from astronomy_types import (
    Anomaly,
    ArgumentOfPerigee,
    Distance,
    Eccentricity,
    Inclination,
    OrbitalElements,
    Radians,
    Ratio,
    RightAscension,
    Scalar,
    SemiMajorAxis,
    TrueAnomaly,
)

DISTANCE_SCALE_KM = 12_824.9333333

EARTH_RADIUS_KM = Distance(Scalar(6_371.0))
INITIAL_ALTITUDE_KM = Distance(Scalar(280_000.0))
TARGET_ALTITUDE_KM = Distance(Scalar(384_400.0 - 6_371.0))


def scaled_distance(distance_km: Distance) -> Distance:
    return Distance(Scalar(distance_km / DISTANCE_SCALE_KM))


if __name__ == "__main__":
    p = ArgumentOfPerigee(Radians(Scalar(math.radians(35))))
    build_hohmann_transfer_2d_perifocal_figure(
        settings=OrbitPlot2DSettings(
            distance_scale_km=DISTANCE_SCALE_KM,
        ),
        initial_orbit=OrbitalElements(
            Inclination(Radians(Scalar(0))),
            RightAscension(Radians(Scalar(0))),
            p,
            SemiMajorAxis(
                scaled_distance(
                    orbit_radius(
                        INITIAL_ALTITUDE_KM,
                        EARTH_RADIUS_KM,
                    )
                )
            ),
            Eccentricity(Ratio(Scalar(0.6))),
            TrueAnomaly(Anomaly(Radians(Scalar(0)))),
        ),
        final_orbit=OrbitalElements(
            Inclination(Radians(Scalar(0))),
            RightAscension(Radians(Scalar(0))),
            p,
            SemiMajorAxis(
                scaled_distance(
                    orbit_radius(
                        TARGET_ALTITUDE_KM,
                        EARTH_RADIUS_KM,
                    )
                )
            ),
            Eccentricity(Ratio(Scalar(0.1))),
            TrueAnomaly(Anomaly(Radians(Scalar(0)))),
        ),
        gravitational_parameter=EARTH_MU_KM_CUBED,
        start_apsis=TransferApsis.APOAPSIS,
    ).show()
