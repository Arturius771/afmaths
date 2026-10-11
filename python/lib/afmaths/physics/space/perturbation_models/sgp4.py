from astronomy_types import (
    FullDate,
    JulianDate,
    PositionVector,
    Scalar,
    Second,
    StateVector,
    Vector3D,
    VelocityVector,
)
from sgp4.api import Satrec, jday

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
    """Compute the Julian date from a FullDate using the SGP4 jday function."""
    jd1, jd2 = sgp4_julian_date(fulldate)
    return JulianDate(Scalar(jd1 + jd2))


def sgp4_julian_date(fulldate: FullDate):
    """Compute the Julian date from a FullDate using the SGP4 jday function."""
    return jday(
        fulldate.date.year,
        fulldate.date.month,
        fulldate.date.day,
        fulldate.time.hour,
        fulldate.time.minute,
        fulldate.time.second,
    )


def state_vector_from_sgp4_result(r: PositionVector, v: VelocityVector) -> StateVector:
    """Convert SGP4 position and velocity vectors to a StateVector."""
    position = position_vector_from_vector(
        Vector3D(
            metres_from_kilometres(r.x),
            metres_from_kilometres(r.y),
            metres_from_kilometres(r.z),
        )
    )
    velocity = velocity_vector_from_vector(
        Vector3D(
            metres_per_second_from_kilometres_per_second(v.x),
            metres_per_second_from_kilometres_per_second(v.y),
            metres_per_second_from_kilometres_per_second(v.z),
        )
    )

    return make_state_vector(position, velocity)


def state_vector_from_satrec(satrec: Satrec) -> StateVector:
    """Compute the state vector of the satellite at its epoch."""
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
) -> StateVector:
    """Compute the state vector of the satellite at a given time offset from the epoch."""
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
    """Create a Satrec object from a TLE string."""
    return Satrec.twoline2rv(tle_line_one(tle), tle_line_two(tle))
