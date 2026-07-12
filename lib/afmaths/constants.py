import math
from typing import Generic, NewType

from astronomy_types import (
    T,
    Acceleration,
    Anomaly,
    ArgumentOfPeriapsis,
    Coordinate3D,
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
)

from afmaths.operation import exponentiate, multiply, negate

EARTH_MU_KM_CUBED = GravitationalParameter(Scalar(398600.5))  # km^3 / s^2
EARTH_RADIUS_KM = Distance(Scalar(6378.0))  # km
MOON_ELEMENTS = OrbitalElements(
    Inclination(Radians(Scalar(0.08956146531375098))),
    RightAscension(Radians(Scalar(5.765000161307142))),
    ArgumentOfPeriapsis(Radians(Scalar(1.9751206723485106))),
    SemiMajorAxis(Distance(Scalar(388470.7933846703))),
    Eccentricity(Ratio(Scalar(0.04483641146974054))),
    TrueAnomaly(Anomaly(Radians(Scalar(4.171189773145077)))),
)
EXAMPLE_ELEMENTS = OrbitalElements(
    Inclination(Radians(Scalar(math.radians(1.145)))),
    RightAscension(Radians(Scalar(3.024483909022929))),
    ArgumentOfPeriapsis(Radians(Scalar(1.5))),
    SemiMajorAxis(Distance(Scalar(384448))),
    Eccentricity(Ratio(Scalar(0.549006))),
    TrueAnomaly(Anomaly(Radians(Scalar(4.1)))),
)
SATELLITE_EXAMPLE_ELEMENTS = OrbitalElements(
    Inclination(Radians(Scalar(math.radians(75)))),
    RightAscension(Radians(Scalar(1.2))),
    ArgumentOfPeriapsis(Radians(Scalar(0.5))),
    SemiMajorAxis(Distance(Scalar(368470.7933846703))),
    Eccentricity(Ratio(Scalar(0.05449006))),
    TrueAnomaly(Anomaly(Radians(Scalar(1)))),
)
SPEED_OF_LIGHT_METRES_PER_SECONDS = 299792458
PLANCK_CONSTANT = multiply(6.62607004)(exponentiate(negate(34))(10))
GRAVITATIONAL_CONSTANT = multiply(6.67430)(exponentiate(negate(11))(10))  # 6.67430e-11
STANDARD_GRAVITY = Acceleration(Scalar(9.80665))  # m/s
STEFAN_BOLTZMANN_CONSTANT = multiply(5.670367)(exponentiate(negate(8))(10))
UNIT_VECTOR_XY_PLANE = Vector3D[Scalar](Scalar(0), Scalar(0), Scalar(1))
ITRS_EXAMPLE_POSITION: list[Coordinate3D[Scalar]] = [
    Coordinate3D(x=Scalar(6790.0), y=Scalar(0.0), z=Scalar(0.0)),
    Coordinate3D(x=Scalar(0.0), y=Scalar(6790.0), z=Scalar(0.0)),
    Coordinate3D(x=Scalar(-6790.0), y=Scalar(0.0), z=Scalar(0.0)),
    Coordinate3D(x=Scalar(0.0), y=Scalar(-6790.0), z=Scalar(0.0)),
    Coordinate3D(x=Scalar(4153.518707), y=Scalar(732.377413), z=Scalar(5321.278575)),
    Coordinate3D(x=Scalar(1091.593504), y=Scalar(-4073.882417), z=Scalar(5321.278575)),
    Coordinate3D(
        x=Scalar(-3230.864009), y=Scalar(-2711.016798), z=Scalar(-5321.278575)
    ),
    Coordinate3D(x=Scalar(2982.288913), y=Scalar(2982.288913), z=Scalar(-5321.278575)),
]
ISS_TLE_EXAMPLE = (
    "1 25544U 98067A   26191.34711344  .00005681  00000-0  11131-3 0  9996"
    "2 25544  51.6302 185.4700 0006688 278.6359  81.3872 15.48968037575346"
)
ISS_NORAD_ID = 25544
GALILEO_7_NORAD_ID = 40544
MOLNIYA_3_50_NORAD_ID = 25847
EUTELSAT_EUTE_117_NORAD_ID = 39122
BEIDOU_IGSO_6 = 41434
SECONDS_PER_DAY = 86400
MINUTES_PER_DAY = 1440
HOURS_PER_DAY = 24
SECONDS_PER_MINUTE = 60
