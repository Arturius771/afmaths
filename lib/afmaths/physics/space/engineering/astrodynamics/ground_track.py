import math
from astronomy_types import (
    Distance,
    Epoch,
    GeographicCoordinates,
    JulianDate,
    Minute,
    OrbitalElements,
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
from afmaths.physics.space.astronomy.time_functions import (
    epoch_offset,
    minutes_from_seconds,
)
from afmaths.physics.space.celestial_mechanics import (
    orbital_direction_from_inclination,
    orbital_period,
    state_vector_at_time,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    orbital_period_from_tle,
    parse_julian_date,
)
from afmaths.physics.space.transformations import (
    itrs_position_from_gcrs_position,
    itrs_positions_from_gcrs_position,
    transform_geographic_coordinates_from_itrs,
)
from afmaths.physics.space.type_conversion_helpers import degrees_from_radians
from afmaths.types import OrbitalDirection


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


def earth_start_of_orbit_coordinates(
    orbital_elements: OrbitalElements,
    epoch: Epoch,
    number_of_orbits: int,
) -> list[GeographicCoordinates]:
    if number_of_orbits < 1:
        return []

    period = orbital_period(orbital_elements.semi_major_axis)

    coordinates = []

    for orbit_index in range(number_of_orbits):
        elapsed_time = Second(Scalar(orbit_index * float(period)))

        gcrs_position = state_vector_at_time(
            orbital_elements,
            elapsed_time,
        ).position

        itrs_position = itrs_position_from_gcrs_position(
            epoch_offset(epoch, elapsed_time),
            gcrs_position,
        )

        coordinates.append(earth_geographic_coordinate_from_itrs(itrs_position))

    return coordinates


def ground_station_cardinal_points(
    ground_station: GeographicCoordinates, range: Distance
) -> list[GeographicCoordinates]:
    """
    Calculate the cardinal points (N, E, S, W) around a ground station given a range.

    This is currently a simple approximation and does not account for the Earth's curvature or other geodetic factors. For more accurate calculations, consider using geospatial libraries or more complex algorithms.
    """
    lat = ground_station.latitude
    lon = ground_station.longitude

    # Calculate the cardinal points
    north = GeographicCoordinates(y=Degrees(Scalar(lat + range)), x=lon)
    east = GeographicCoordinates(y=Degrees(Scalar(lat)), x=Degrees(Scalar(lon + range)))
    south = GeographicCoordinates(y=Degrees(Scalar(lat - range)), x=lon)
    west = GeographicCoordinates(y=Degrees(Scalar(lat)), x=Degrees(Scalar(lon - range)))

    return [north, east, south, west]


def general_orbital_characteristics(tle: str) -> str:
    direction = orbital_direction_from_inclination(
        orbital_elements_from_tle(tle).inclination
    )
    orbital_period = orbital_period_from_tle(tle)

    return f"Drift: { westward_drift_from_angular_velocity_and_period   (orbital_period):.2f}° | Direction: {"Prograde" if direction == OrbitalDirection.PROGRADE else "Retrograde"} | Epoch (JD): {parse_julian_date(tle)} | Period: {orbital_period:.0f}s"
