import math

from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Coordinate3D,
    Day,
    Distance,
    Eccentricity,
    Epoch,
    Inclination,
    JulianDate,
    MeanAnomaly,
    MeanMotion,
    PositionVector,
    Radians,
    Rate,
    Ratio,
    RightAscension,
    Scalar,
)

from afmaths.operation import divide_by
from afmaths.physics.space.type_conversion_helpers import (
    make_vector3d,
    radians_from_degrees,
    radians_from_string,
)
from afmaths.tensors import vector_magnitude_3d, vector_subtract_3d

# 1 25544U 98067A   26191.34711344  .00005681  00000-0  11131-3 0  9996
# 2 25544  51.6302 185.4700 0006688 278.6359  81.3872 15.48968037575346

# ['1', '25544U', '98067A', '26191.34711344', '.00005681', '00000-0', '11131-3', '0', '99962', '25544', '51.6302', '185.4700', '0006688', '278.6359', '81.3872', '15.48968037575346']


def orbital_period_mean_motion(n_per_day: MeanMotion) -> Day:
    return divide_by(n_per_day)(1)


def non_empty_str(string: str) -> bool:
    return string != ""


def split_tle(tle: str) -> list[str]:
    return list(filter(non_empty_str, tle.split(" ")))


def parse_epoch(tle: str) -> Epoch:
    return Epoch(JulianDate(Scalar(float(split_tle(tle)[3]))))


def parse_inclinatition(tle: str) -> Inclination:
    return Inclination(radians_from_string(split_tle(tle)[10]))


def parse_right_ascension_ascending_node(tle: str) -> RightAscension:
    return RightAscension(Radians(radians_from_string(split_tle(tle)[11])))


def parse_eccentricity(tle: str) -> Eccentricity:
    return Eccentricity(Ratio(Scalar(float("0." + split_tle(tle)[12]))))


def parse_argument_of_periapsis(tle: str) -> ArgumentOfPeriapsis:
    return ArgumentOfPeriapsis(Radians(radians_from_string(split_tle(tle)[13])))


def parse_mean_anomaly(tle: str) -> MeanAnomaly:
    return MeanAnomaly(Anomaly(radians_from_string(split_tle(tle)[14])))


def parse_mean_motion(tle: str) -> MeanMotion:
    return MeanMotion(Rate(Scalar(float(split_tle(tle)[15]))))
