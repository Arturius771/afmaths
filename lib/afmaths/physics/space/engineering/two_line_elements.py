from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Day,
    Eccentricity,
    FullDate,
    GravitationalParameter,
    Inclination,
    MeanAnomaly,
    MeanMotion,
    OrbitalElements,
    Radians,
    Rate,
    Ratio,
    RightAscension,
    Scalar,
    Second,
    StateVector,
    Year,
)

from afmaths.constants import EARTH_MU_KM_CUBED
from afmaths.operation import divide_by
from afmaths.physics.space.astronomy.time_functions import (
    date_from_day_number,
    time_from_percentage,
)
from afmaths.physics.space.celestial_mechanics import (
    eccentric_anomaly_solved,
    newtons_method_eccentric_anomaly,
    orbital_period,
    orbital_period_from_mean_motion,
    semi_major_axis_from_period,
    state_vector_from_orbital_elements,
    true_anomaly_from_eccentric_anomaly,
)
from afmaths.physics.space.type_conversion_helpers import (
    radians_from_string,
)

# 1 25544U 98067A   26191.34711344  .00005681  00000-0  11131-3 0  9996
# 2 25544  51.6302 185.4700 0006688 278.6359  81.3872 15.48968037575346

# ['1', '25544U', '98067A', '26191.34711344', '.00005681', '00000-0', '11131-3', '0', '99962', '25544', '51.6302', '185.4700', '0006688', '278.6359', '81.3872', '15.48968037575346']


def orbital_period_mean_motion(n_per_day: MeanMotion) -> Day:
    return divide_by(n_per_day)(1)


# def non_empty_str(string: str) -> bool:
#     return string != ""


# def split_tle(tle: str) -> list[str]:
#     return list(filter(non_empty_str, tle.split(" ")))


COLUMN_LINE_NUMBER = 0
SATELLITE_CATALOGUE_NUMBER = 2
COLUMN_CHECKSUM = 68


# SATELLITE_CATALOGUE_NUMBER_END = 6
COLUMN_1_ELSET = 7
COLUMN_1_INTERNATIONAL_DESIGNATOR = 9
# COLUMN_1_INTERNATIONAL_DESIGNATOR_END = 16
COLUMN_1_EPOCH = 18
# COLUMN_1_EPOCH_END = 31
COLUMN_1_FIRST_DX_MEAN_MOTION = 33
# COLUMN_1_FIRST_DX_MEAN_MOTION_END = 42
COLUMN_1_SECOND_DX_MEAN_MOTION = 44
# COLUMN_1_SECOND_DX_MEAN_MOTION_END = 51
COLUMN_1_DRAG_TERM = 53
COLUMN_1_ELEMENT_SET_TYPE = 62
COLUMN_1_ELEMENT_NUMBER = 64

COLUMN_2_INCLINATION = 8
COLUMN_2_RAAN = 17
COLUMN_2_ECCENTRICITY = 26
COLUMN_2_ARGUMENT_PERIAPSIS = 34
COLUMN_2_MEAN_ANOMALY = 43
COLUMN_2_MEAN_MOTION = 52
COLUMN_2_REVOLUTION_NUMBER = 63


def tle_column_one(tle: str) -> str:
    return tle[0:69]


def tle_column_two(tle: str) -> str:
    return tle[69:].lstrip("\r\n")


def get_tle_element_from_column(
    tle_column: str, start_index: int, next_index: int
) -> str:
    return tle_column[start_index:next_index].strip()


# region TLE Elements


def parse_norad_id(tle: str) -> str:
    return get_tle_element_from_column(
        tle_column_one(tle), SATELLITE_CATALOGUE_NUMBER, COLUMN_1_ELSET
    )


def parse_epoch(tle: str) -> str:
    return get_tle_element_from_column(
        tle_column_one(tle), COLUMN_1_EPOCH, COLUMN_1_FIRST_DX_MEAN_MOTION
    )


def parse_full_date(tle: str) -> FullDate:
    epoch = parse_epoch(tle)
    year = Year(int(f"20{epoch[:2]}"))
    date = date_from_day_number(int(epoch[2:5]), year)
    time = time_from_percentage(float(f"0.{epoch.split(".")[1]}"))

    return FullDate(date, time)


def parse_inclination(tle: str) -> Inclination:
    return Inclination(
        radians_from_string(
            get_tle_element_from_column(
                tle_column_two(tle), COLUMN_2_INCLINATION, COLUMN_2_RAAN
            )
        )
    )


def parse_right_ascension_ascending_node(tle: str) -> RightAscension:
    return RightAscension(
        Radians(
            radians_from_string(
                get_tle_element_from_column(
                    tle_column_two(tle), COLUMN_2_RAAN, COLUMN_2_ECCENTRICITY
                )
            )
        )
    )


def parse_eccentricity(tle: str) -> Eccentricity:
    return Eccentricity(
        Ratio(
            Scalar(
                float(
                    "0."
                    + get_tle_element_from_column(
                        tle_column_two(tle),
                        COLUMN_2_ECCENTRICITY,
                        COLUMN_2_ARGUMENT_PERIAPSIS,
                    )
                )
            )
        )
    )


def parse_argument_of_periapsis(tle: str) -> ArgumentOfPeriapsis:
    return ArgumentOfPeriapsis(
        Radians(
            radians_from_string(
                get_tle_element_from_column(
                    tle_column_two(tle),
                    COLUMN_2_ARGUMENT_PERIAPSIS,
                    COLUMN_2_MEAN_ANOMALY,
                )
            )
        )
    )


def parse_mean_anomaly(tle: str) -> MeanAnomaly:
    return MeanAnomaly(
        Anomaly(
            radians_from_string(
                get_tle_element_from_column(
                    tle_column_two(tle), COLUMN_2_MEAN_ANOMALY, COLUMN_2_MEAN_MOTION
                )
            )
        )
    )


def parse_mean_motion_per_day(tle: str) -> MeanMotion:
    return MeanMotion(
        Rate(
            Scalar(
                float(
                    get_tle_element_from_column(
                        tle_column_two(tle),
                        COLUMN_2_MEAN_MOTION,
                        COLUMN_2_REVOLUTION_NUMBER,
                    )
                )
            )
        )
    )


def orbital_period_from_tle(
    tle: str, mu: GravitationalParameter = EARTH_MU_KM_CUBED
) -> Second:
    return orbital_period(orbital_elements_from_tle(tle).semi_major_axis, mu)


def orbital_elements_from_tle(
    tle: str, mu: GravitationalParameter = EARTH_MU_KM_CUBED
) -> OrbitalElements:
    e = parse_eccentricity(tle)

    return OrbitalElements(
        parse_inclination(tle),
        parse_right_ascension_ascending_node(tle),
        parse_argument_of_periapsis(tle),
        semi_major_axis_from_period(
            orbital_period_from_mean_motion(parse_mean_motion_per_day(tle)), mu
        ),
        e,
        true_anomaly_from_eccentric_anomaly(
            eccentric_anomaly_solved(
                newtons_method_eccentric_anomaly, e, parse_mean_anomaly(tle)
            )[0],
            e,
        ),
    )


def orbital_state_vectors_from_tle(tle) -> StateVector:
    return state_vector_from_orbital_elements(orbital_elements_from_tle(tle))
