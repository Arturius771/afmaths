import math
from typing import Generic, NewType

from astronomy_types import (
    T,
    Acceleration,
    Anomaly,
    ArgumentOfPeriapsis,
    Eccentricity,
    Enum,
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
    Vector2D,
    Vector3D,
    Velocity,
    dataclass,
)

from afmaths.operation import exponentiate, multiply, negate

EARTH_MU_KM_CUBED = GravitationalParameter(Scalar(398600.5))  # km^3 / s^2
EARTH_RADIUS_KM = Distance(Scalar(6378.0))  # km
EXAMPLE_ELEMENTS = OrbitalElements(
    Inclination(Radians(Scalar(math.radians(0)))),
    RightAscension(Radians(Scalar(3.024483909022929))),
    ArgumentOfPeriapsis(Radians(Scalar(0))),
    SemiMajorAxis(Distance(Scalar(384748))),
    Eccentricity(Ratio(Scalar(0.0549006))),
    TrueAnomaly(Anomaly(Radians(Scalar(30)))),
)
# OTHER_EXAMPLE_ELEMENTS = OrbitalElements(
#     Inclination(Radians(Scalar(math.radians(5.145)))),
#     RightAscension(Radians(Scalar(3.024483909022929))),
#     ArgumentOfPeriapsis(Radians(Scalar(0))),
#     SemiMajorAxis(Distance(Scalar(384748))),
#     Eccentricity(Ratio(Scalar(0.0549006))),
#     TrueAnomaly(Anomaly(Radians(Scalar(2.987554518980773)))),
# )
OTHER_EXAMPLE_ELEMENTS = OrbitalElements(
    Inclination(Radians(Scalar(math.radians(75)))),
    RightAscension(Radians(Scalar(1))),
    ArgumentOfPeriapsis(Radians(Scalar(0.6))),
    SemiMajorAxis(Distance(Scalar(260000))),
    Eccentricity(Ratio(Scalar(0.5449006))),
    TrueAnomaly(Anomaly(Radians(Scalar(1)))),
)
# OTHER_EXAMPLE_ELEMENTS = OrbitalElements(
#     Inclination(Radians(Scalar(math.radians(0)))),
#     RightAscension(Radians(Scalar(3.024483909022929))),
#     ArgumentOfPeriapsis(Radians(Scalar(0))),
#     SemiMajorAxis(Distance(Scalar(384748))),
#     Eccentricity(Ratio(Scalar(0.0549006))),
#     TrueAnomaly(Anomaly(Radians(Scalar(19)))),
# )
SPEED_OF_LIGHT_METRES_PER_SECONDS = 299792458
PLANCK_CONSTANT = multiply(6.62607004)(exponentiate(negate(34))(10))
GRAVITATIONAL_CONSTANT = multiply(6.67430)(exponentiate(negate(11))(10))  # 6.67430e-11
STANDARD_GRAVITY = Acceleration(Scalar(9.80665))  # m/s
STEFAN_BOLTZMANN_CONSTANT = multiply(5.670367)(exponentiate(negate(8))(10))

Mass = NewType("Mass", float)
Pressure = NewType("Pressure", float)
Force = NewType("Force", float)
Area = NewType("Area", Scalar)
TransformationMatrix2D = NewType("TransformationMatrix2D", Vector2D[Vector2D[Scalar]])
TransformationMatrix3D = NewType("TransformationMatrix3D", Vector3D[Vector3D[Scalar]])
DeltaV = NewType("DeltaV", Velocity)
EarthCentredInertialFrame = NewType("EarthCentredInertialFrame", Vector3D[Scalar])
Momentum = NewType("Momentum", Scalar)
Force = NewType("Force", Scalar)


class BurnDirection(Enum):
    PROGRADE = "prograde"
    RETROGRADE = "retrograde"
    RADIAL = "radial"
    ANTIRADIAl = "antiradial"
    NORMAL = "normal"
    ANTINORMAL = "antinormal"
