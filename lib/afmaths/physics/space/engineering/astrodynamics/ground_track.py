import math
from astronomy_types import (
    Distance,
    Epoch,
    GeographicCoordinates,
    OrbitalElements,
    PositionVector,
    Scalar,
    Second,
    Inclination,
    Latitude,
    Degrees,
)

from afmaths.constants import (
    SECONDS_PER_DAY,
)
from afmaths.operation import (
    negate,
)
from afmaths.physics.space.astronomy.time_functions import (
    epoch_offset,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    state_vector_at_time,
)
from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.engineering.astrodynamics.utils import (
    general_orbital_characteristics_from_elements,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    parse_julian_date,
)
from afmaths.physics.space.transformations import (
    itrf_position_from_gcrs_position,
    itrf_positions_from_gcrs_position,
    geographic_coordinates_from_itrf,
)
from afmaths.afmath_types import GroundStation


def max_latitude(i: Inclination) -> Latitude:
    """In degrees"""
    return Degrees(Scalar(math.degrees(i)))


def min_latitude(i: Inclination) -> Latitude:
    """In degrees"""
    return Degrees(Scalar(negate(math.degrees(i))))


def earth_geographic_coordinate_from_itrf(
    itrf: PositionVector,
) -> GeographicCoordinates:
    """Converts ITRS cartesian coordinates to geographic Lat/Lon (degrees). Useful for ground track plotting."""
    return geographic_coordinates_from_itrf(itrf)


def earth_ground_track_positions(
    gcrs_positions: list[PositionVector],
    epoch: Epoch,
) -> list[PositionVector]:
    """Transforms a list of GCRS positions to ITRS positions at a given epoch."""

    return itrf_positions_from_gcrs_position(gcrs_positions, epoch)


def orbits_per_day(orbital_period, day_duration: Second = SECONDS_PER_DAY) -> float:
    """Calculates the number of orbits completed in a day based on the orbital period."""
    return day_duration / orbital_period


def earth_start_of_orbit_coordinates(
    orbital_elements: OrbitalElements,
    epoch: Epoch,
    number_of_orbits: int,
) -> list[GeographicCoordinates]:
    """Calculates the geographic coordinates of the start of each orbit for a given number of orbits based on the orbital elements and epoch.

    Start is defined as the point where the satellite crosses the ascending node.
    """
    if number_of_orbits < 1:
        return []

    period = orbital_period(orbital_elements.semi_major_axis)

    coordinates = []

    for orbit_index in range(number_of_orbits):
        elapsed_time = Second(Scalar(orbit_index * float(period)))

        # GCRS because the elements are derived from the GCRS frame.
        gcrs_intertial_position = state_vector_at_time(
            orbital_elements,
            elapsed_time,
        ).position

        itrf_position = itrf_position_from_gcrs_position(
            epoch_offset(epoch, elapsed_time),
            gcrs_intertial_position,
        )

        coordinates.append(earth_geographic_coordinate_from_itrf(itrf_position))

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


# def time_of_pass(ground_station: GroundStation, orbital_elements: OrbitalElements, epoch: Epoch) -> FullDate:


def ground_track_passes_station(
    ground_station: GroundStation,
    ground_track: list[GeographicCoordinates],
    margin: Degrees = Degrees(Scalar(5)),
) -> bool:
    """
    Determines if a ground track passes within a certain margin of a ground station.

    Args:
        ground_station (GroundStation): The geographic coordinates of the ground station.
        ground_track (list[GeographicCoordinates]): A list of geographic coordinates representing the ground track.
        margin (Degrees): The margin in degrees to consider for proximity.

    Returns:
        bool: True if the ground track passes within the margin of the ground station, False otherwise.
    """
    for point in ground_track:
        lat_diff = abs(point.latitude - ground_station.coordinates.latitude)
        lon_diff = abs(point.longitude - ground_station.coordinates.longitude)

        if lat_diff <= margin and lon_diff <= margin:
            return True

    return False


def general_orbital_characteristics_from_tle(tle: str) -> str:
    """Extracts general orbital characteristics from a TLE string and returns them as a formatted string."""
    elements = orbital_elements_from_tle(tle)

    return f"Epoch (JD): {parse_julian_date(tle)} | {general_orbital_characteristics_from_elements(elements)}"
