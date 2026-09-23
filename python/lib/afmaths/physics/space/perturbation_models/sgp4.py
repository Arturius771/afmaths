from sgp4.api import Satrec, jday
from astronomy_types import FullDate, JulianDate, Scalar, Second, Vector3D

from afmaths.constants import SECONDS_PER_DAY
from afmaths.physics.space.engineering.two_line_elements import (
    tle_line_one,
    tle_line_two,
)
from afmaths.physics.space.type_conversion_helpers import (
    make_state_vector,
    position_vector_from_vector,
    velocity_vector_from_vector,
)
from afmaths.physics.space.unit_conversion_helpers import (
    metres_from_kilometres,
    metres_per_second_from_kilometres_per_second,
)


def julian_date_from_jday(fulldate: FullDate) -> JulianDate:
    jd1, jd2 = sgp4_julian_date(fulldate)
    return JulianDate(Scalar(jd1 + jd2))


def sgp4_julian_date(fulldate: FullDate):
    return jday(
        fulldate.date.year,
        fulldate.date.month,
        fulldate.date.day,
        fulldate.time.hour,
        fulldate.time.minute,
        fulldate.time.second,
    )


def state_vector_from_sgp4_result(r, v):
    position = position_vector_from_vector(
        Vector3D(
            metres_from_kilometres(r[0]),
            metres_from_kilometres(r[1]),
            metres_from_kilometres(r[2]),
        )
    )
    velocity = velocity_vector_from_vector(
        Vector3D(
            metres_per_second_from_kilometres_per_second(v[0]),
            metres_per_second_from_kilometres_per_second(v[1]),
            metres_per_second_from_kilometres_per_second(v[2]),
        )
    )

    return make_state_vector(position, velocity)


def state_vector_from_satrec(satrec: Satrec):
    e, r, v = satrec.sgp4(
        satrec.jdsatepoch,
        satrec.jdsatepochF,
    )
    if e != 0:
        raise ValueError(f"SGP4 propagation error: {e}")

    return state_vector_from_sgp4_result(r, v)


def state_vector_from_satrec_at_time(
    satrec: Satrec,
    time_offset: Second,
):
    day_offset, fractional_day = divmod(
        satrec.jdsatepochF + float(time_offset) / SECONDS_PER_DAY,
        1.0,
    )

    e, r, v = satrec.sgp4(
        satrec.jdsatepoch + day_offset,
        fractional_day,
    )
    if e != 0:
        raise ValueError(f"SGP4 propagation error: {e}")

    return state_vector_from_sgp4_result(r, v)


def sgp4_satrec(tle: str) -> Satrec:
    return Satrec.twoline2rv(tle_line_one(tle), tle_line_two(tle))
