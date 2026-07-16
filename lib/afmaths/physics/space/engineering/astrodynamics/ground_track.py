import math
from astronomy_types import (
    Epoch,
    GeographicCoordinates,
    JulianDate,
    Minute,
    PositionVector,
    Radians,
    Scalar,
    Second,
    Inclination,
    Latitude,
    Degrees,
    MeanMotion,
)

from afmaths.constants import EARTH_ANGULAR_VELOCITY, MINUTES_PER_DAY, SECONDS_PER_DAY
from afmaths.operation import (
    divide_by,
    multiply,
    negate,
)
from afmaths.physics.space.astronomy.time_functions import minutes_from_seconds
from afmaths.physics.space.transformations import (
    itrs_positions_from_gcrs_position,
    transform_geographic_coordinates_from_itrs,
)
from afmaths.physics.space.type_conversion_helpers import degrees_from_radians


def max_latitude(i: Inclination) -> Latitude:
    return Degrees(Scalar(math.degrees(i)))


def min_latitude(i: Inclination) -> Latitude:
    return Degrees(Scalar(negate(math.degrees(i))))


def westward_drift_from_mean_motion(n: MeanMotion) -> Degrees:
    return Degrees(Scalar(multiply(360)(divide_by(n)(1))))


def westward_drift_from_angular_velocity_and_period(
    orbital_period: Second,
    body_angular_velocity: Radians = EARTH_ANGULAR_VELOCITY,
) -> Degrees:
    return degrees_from_radians(multiply(body_angular_velocity)(orbital_period))


def earth_geographic_coordinate_from_itrs(
    itrs: PositionVector,
) -> GeographicCoordinates:
    return transform_geographic_coordinates_from_itrs(itrs)


def earth_ground_track_positions(
    gcrs_positions: list[PositionVector],
    epoch: Epoch,
) -> list[PositionVector]:

    return itrs_positions_from_gcrs_position(gcrs_positions, epoch)


def orbits_per_day(orbital_period, day_duration: Second = SECONDS_PER_DAY) -> float:
    return day_duration / orbital_period


def earth_start_of_orbit_positions(
    gcrs_positions: list[PositionVector],
    orbital_period: Second,
) -> list[PositionVector]:
    minutes_per_orbit = float(minutes_from_seconds(orbital_period))

    total_orbits_in_positions = math.ceil(len(gcrs_positions) / minutes_per_orbit)

    start_indices = [
        math.floor(orbit * minutes_per_orbit)
        for orbit in range(total_orbits_in_positions)
    ]

    return [
        gcrs_positions[index] for index in start_indices if index < len(gcrs_positions)
    ]
