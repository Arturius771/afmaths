import math

from astronomy_types import (
    Anomaly,
    ArgumentOfPerigee,
    Distance,
    Eccentricity,
    EquatorialCoordinates,
    Inclination,
    OrbitalElements,
    Radians,
    Ratio,
    RightAscension,
    Scalar,
    SemiMajorAxis,
    TrueAnomaly,
)

EXAMPLE_ELEMENTS = OrbitalElements(
    Inclination(Radians(Scalar(math.radians(5.145)))),
    RightAscension(Radians(Scalar(3.024483909022929))),
    ArgumentOfPerigee(Radians(Scalar(8.8))),
    SemiMajorAxis(Distance(Scalar(384748))),
    Eccentricity(Ratio(Scalar(0.0549006))),
    TrueAnomaly(Anomaly(Radians(Scalar(2.987554518980773)))),
)


# ----------
# Thermal subsystem
# ----------
def beta_angle(sun: EquatorialCoordinates, orbit: OrbitalElements) -> Radians:
    value = math.cos(sun.declination) * math.sin(orbit.inclination) * math.sin(
        orbit.right_ascension_of_ascending_node - sun.right_ascension
    ) + math.sin(sun.declination) * math.cos(orbit.inclination)

    # Prevent floating point drift errors at values close to +/-1.
    value = max(-1.0, min(1.0, value))

    return Radians(Scalar(math.asin(value)))


if __name__ == "__main__":
    print(
        beta_angle(
            EquatorialCoordinates(Radians(Scalar(12)), Radians(Scalar(12))),
            EXAMPLE_ELEMENTS,
        )
    )
