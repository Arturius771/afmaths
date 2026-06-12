import math
from typing import NewType

from astronomy_types import (
    Anomaly,
    ArgumentOfPerigee,
    Eccentricity,
    GravitationalParameter,
    Distance,
    Inclination,
    OrbitalElements,
    Radians,
    Ratio,
    RightAscension,
    Scalar,
    SemiMajorAxis,
    TrueAnomaly,
    Vector3D,
    Velocity,
)

from afmaths.operation import exponentiate, multiply

EARTH_MU_KM_CUBED = GravitationalParameter(Scalar(398600.5))  # km^3 / s^2
EARTH_RADIUS_KM = Distance(Scalar(6378.0))  # km
EXAMPLE_ELEMENTS = OrbitalElements(
    Inclination(Radians(Scalar(math.radians(0)))),
    RightAscension(Radians(Scalar(3.024483909022929))),
    ArgumentOfPerigee(Radians(Scalar(0))),
    SemiMajorAxis(Distance(Scalar(384748))),
    Eccentricity(Ratio(Scalar(0.0549006))),
    TrueAnomaly(Anomaly(Radians(Scalar(30)))),
)
# OTHER_EXAMPLE_ELEMENTS = OrbitalElements(
#     Inclination(Radians(Scalar(math.radians(5.145)))),
#     RightAscension(Radians(Scalar(3.024483909022929))),
#     ArgumentOfPerigee(Radians(Scalar(0))),
#     SemiMajorAxis(Distance(Scalar(384748))),
#     Eccentricity(Ratio(Scalar(0.0549006))),
#     TrueAnomaly(Anomaly(Radians(Scalar(2.987554518980773)))),
# )
OTHER_EXAMPLE_ELEMENTS = OrbitalElements(
    Inclination(Radians(Scalar(math.radians(75)))),
    RightAscension(Radians(Scalar(1))),
    ArgumentOfPerigee(Radians(Scalar(0))),
    SemiMajorAxis(Distance(Scalar(250000))),
    Eccentricity(Ratio(Scalar(0.5449006))),
    TrueAnomaly(Anomaly(Radians(Scalar(30)))),
)
SPEED_OF_LIGHT_METRES_PER_SECONDS = 299792458
PLANCK_CONSTANT = multiply(6.62607004)(exponentiate(-34)(10))
GRAVITATIONAL_CONSTANT = multiply(6.67430)(exponentiate(-11)(10))  # 6.67430e-11
STANDARD_GRAVITY = 9.80665  # m/s

Mass = NewType("Mass", float)
Pressure = NewType("Pressure", float)
Force = NewType("Force", float)
Area = NewType("Area", Scalar)
RotationMatrix = NewType("RotationMatrix", Vector3D[Vector3D[Scalar]])
DeltaV = NewType("DeltaV", Velocity)
EarthCentredInertial = NewType("EarthCentredInertial", Vector3D[Scalar])
