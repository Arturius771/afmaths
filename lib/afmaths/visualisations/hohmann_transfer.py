import math

from afmaths.constants import EARTH_MU_KM_CUBED
from afmaths.physics.space.celestial_mechanics import orbit_radius
from afmaths.visualisations.base_orbit_plot import (
    HohmannTransfer2DPerifocalPlot,
    TransferApsis,
)
from afmaths.visualisations.helpers import OrbitPlot2DSettings
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
INITIAL_ALTITUDE_KM = Distance(Scalar(50_000.0))
TARGET_ALTITUDE_KM = Distance(Scalar(384_400.0 - 6_371.0))


def scaled_distance(distance_km: Distance) -> Distance:
    return Distance(Scalar(distance_km / DISTANCE_SCALE_KM))


if __name__ == "__main__":
    settings = OrbitPlot2DSettings(
        distance_scale_km=DISTANCE_SCALE_KM,
    )

    initial_radius_km = orbit_radius(
        INITIAL_ALTITUDE_KM,
        EARTH_RADIUS_KM,
    )

    final_radius_km = orbit_radius(
        TARGET_ALTITUDE_KM,
        EARTH_RADIUS_KM,
    )

    initial_radius_plot = scaled_distance(initial_radius_km)
    final_radius_plot = scaled_distance(final_radius_km)

    initial_orbit = OrbitalElements(
        Inclination(Radians(Scalar(0))),
        RightAscension(Radians(Scalar(0))),
        ArgumentOfPerigee(Radians(Scalar(math.radians(35)))),
        SemiMajorAxis(initial_radius_plot),
        Eccentricity(Ratio(Scalar(0.25))),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    final_orbit = OrbitalElements(
        Inclination(Radians(Scalar(0))),
        RightAscension(Radians(Scalar(0))),
        initial_orbit.argument_of_periapsis,
        SemiMajorAxis(final_radius_plot),
        Eccentricity(Ratio(Scalar(0.1))),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    HohmannTransfer2DPerifocalPlot(
        settings=settings,
        initial_orbit=initial_orbit,
        final_orbit=final_orbit,
        initial_altitude_km=INITIAL_ALTITUDE_KM,
        target_altitude_km=TARGET_ALTITUDE_KM,
        gravitational_parameter=EARTH_MU_KM_CUBED,
        start_apsis=TransferApsis.PERIAPSIS,
        final_apsis=TransferApsis.APOAPSIS,
    ).show()
