from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Day,
    Eccentricity,
    FullDate,
    Inclination,
    MeanAnomaly,
    MeanMotion,
    Radians,
    Rate,
    Ratio,
    RightAscension,
    Scalar,
    Year,
)

from afmaths.operation import divide_by
from afmaths.physics.space.astronomy.time_functions import (
    date_from_day_number,
    time_from_percentage,
)
from afmaths.physics.space.type_conversion_helpers import (
    radians_from_string,
)

# 1 25544U 98067A   26191.34711344  .00005681  00000-0  11131-3 0  9996
# 2 25544  51.6302 185.4700 0006688 278.6359  81.3872 15.48968037575346

# ['1', '25544U', '98067A', '26191.34711344', '.00005681', '00000-0', '11131-3', '0', '99962', '25544', '51.6302', '185.4700', '0006688', '278.6359', '81.3872', '15.48968037575346']


def orbital_period_mean_motion(n_per_day: MeanMotion) -> Day:
    return divide_by(n_per_day)(1)


def non_empty_str(string: str) -> bool:
    return string != ""


def split_tle(tle: str) -> list[str]:
    return list(filter(non_empty_str, tle.split(" ")))


def parse_epoch(tle: str) -> str:
    return split_tle(tle)[3]


def parse_full_date(tle: str) -> FullDate:
    epoch = parse_epoch(tle)
    year = Year(int(f"20{epoch[:2]}"))
    date = date_from_day_number(int(epoch[2:5]), year)
    time = time_from_percentage(float(f"0.{epoch.split(".")[1]}"))

    return FullDate(date, time)


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
