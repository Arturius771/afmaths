import math
from astronomy_types import (
    Day,
    Distance,
    Epoch,
    FullDate,
    GeographicCoordinates,
    GravitationalParameter,
    OrbitalElements,
    PositionVector,
    Ratio,
    Scalar,
    Second,
    Inclination,
    Latitude,
    Degrees,
    Year,
)

from afmaths.afmath_types import Percentage
from afmaths.constants import (
    EARTH_MU,
    SECONDS_PER_DAY,
)
from afmaths.operation import (
    negate,
    normalised_percentage,
    percentage,
)
from afmaths.physics.space.astronomy.time_functions import (
    epoch_offset,
    greenwich_full_date_from_julian_date,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    apoapsis_true_anomaly,
    periapsis_true_anomaly,
)

from afmaths.physics.space.celestial_mechanics.state_vector import (
    position_vector_at_time,
)
from afmaths.physics.space.celestial_mechanics.time import (
    orbital_period,
    time_to_true_anomaly,
)
from afmaths.physics.space.celestial_mechanics.utils import second_intervals_for_orbits
from afmaths.physics.space.transformations import (
    itrf_position_from_gcrf_position,
    itrf_positions_from_gcrf_position,
    geographic_coordinates_from_itrf,
)
from afmaths.physics.space.type_conversion_helpers import make_date


def max_latitude(i: Inclination) -> Latitude:
    """In degrees"""
    return Degrees(Scalar(math.degrees(i)))


def min_latitude(i: Inclination) -> Latitude:
    """In degrees"""
    return Degrees(Scalar(negate(math.degrees(i))))


def earth_ground_track_positions(
    gcrf_positions: list[PositionVector],
    epoch: Epoch,
) -> list[PositionVector]:
    """Transforms a list of GCRF positions to ITRF positions at a given epoch."""

    return itrf_positions_from_gcrf_position(gcrf_positions, epoch)


def orbits_per_day(orbital_period, day_duration: Second = SECONDS_PER_DAY) -> float:
    """Calculates the number of orbits completed in a day based on the orbital period."""
    return day_duration / orbital_period


def geographic_coordinates_for_orbit(
    orbit: OrbitalElements,
    epoch: Epoch,
    orbit_count: float,
    number_of_points: int,
    time_interval: Second | None = None,
) -> list[GeographicCoordinates]:
    """Calculates the geographic coordinates for a given orbit over a specified number of orbits and points."""
    period = orbital_period(orbit.semi_major_axis)
    duration = Second(Scalar(period * orbit_count))

    elapsed_times = second_intervals_for_orbits(
        Second(Scalar(0)),
        duration,
        number_of_points,
        time_interval,
    )

    return [
        geographic_coordinates_from_itrf(
            itrf_position_from_gcrf_position(
                epoch_offset(epoch, elapsed_time),
                position_vector_at_time(
                    orbit,
                    elapsed_time,
                    EARTH_MU,
                ),
            )
        )
        for elapsed_time in elapsed_times
    ]


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

        # GCRF because the elements are derived from the GCRF frame.
        gcrf_intertial_position = position_vector_at_time(
            orbital_elements,
            elapsed_time,
        )

        itrf_position = itrf_position_from_gcrf_position(
            epoch_offset(epoch, elapsed_time),
            gcrf_intertial_position,
        )

        coordinates.append(geographic_coordinates_from_itrf(itrf_position))

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
    coords: GeographicCoordinates,
    ground_track: list[GeographicCoordinates],
    tolerance: Degrees = Degrees(Scalar(5)),
) -> tuple[bool, Ratio]:
    """
    Determines if a ground track passes within a certain margin of a ground station.

    Args:
        coords (GeographicCoordinates): The geographic coordinates of the ground station.
        ground_track (list[GeographicCoordinates]): A list of geographic coordinates representing the ground track.
        tolerance (Degrees): The tolerance in degrees to consider for proximity.

    Returns:
        bool: True if the ground track passes within the tolerance of the ground station, False otherwise.
    """
    for index, point in enumerate(ground_track):
        lat_diff = abs(point.latitude - coords.latitude)
        lon_diff = abs(point.longitude - coords.longitude)

        if lat_diff <= tolerance and lon_diff <= tolerance:
            return True, normalised_percentage(percentage(index, len(ground_track)))

    return False, Ratio(Scalar(-1))


def orbit_epoch_of_pass(
    coords: GeographicCoordinates,
    orbital_elements: OrbitalElements,
    epoch: Epoch,
    tolerance: Degrees = Degrees(Scalar(5)),
    max_orbit_iterations: int = 50,
) -> tuple[Epoch, int, Ratio] | None:
    """
    Calculate the times when a satellite passes over a ground station based on its orbital elements and the ground station's location.

    Args:
        coords (GeographicCoordinates): The geographic coordinates of the ground station.
        orbital_elements (OrbitalElements): The orbital elements of the satellite.
        epoch (Epoch): The reference epoch for the calculations.
        tolerance (Degrees): The tolerance in degrees for determining a pass.
        max_orbit_iterations (int): The maximum number of orbit iterations to attempt when calculating the pass.
    Returns:
        tuple[Epoch, int, Ratio] | None: The epoch representing the time of pass over the ground station, the iteration count, and the orbit percentage as a ratio, or None if no pass is found.
    """
    # Placeholder implementation. Actual implementation would require complex calculations
    # involving orbital mechanics and ground station visibility.

    for iteration in range(max_orbit_iterations):
        epoch_offset_time = epoch_offset(
            epoch,
            Second(
                Scalar(
                    iteration * float(orbital_period(orbital_elements.semi_major_axis))
                )
            ),
        )

        does_pass, orbit_percent = ground_track_passes_station(
            coords,
            geographic_coordinates_for_orbit(
                orbital_elements,
                epoch_offset_time,
                orbit_count=1,
                number_of_points=500,
            ),
            tolerance,
        )

        if does_pass:
            period = orbital_period(orbital_elements.semi_major_axis)

            pass_elapsed_time = Second(
                Scalar(iteration * float(period) + float(orbit_percent) * float(period))
            )

            return (
                epoch_offset(epoch, pass_elapsed_time),
                iteration,
                orbit_percent,
            )

    return None


def orbit_epoch_of_pass_full_date(
    coords: GeographicCoordinates,
    orbital_elements: OrbitalElements,
    epoch: Epoch,
    tolerance: Degrees = Degrees(Scalar(5)),
    max_orbit_iterations: int = 50,
) -> FullDate | None:
    """
    Calculate the full date when a satellite passes over a ground station based on its orbital elements and the ground station's location.
    """
    result = orbit_epoch_of_pass(
        coords, orbital_elements, epoch, tolerance, max_orbit_iterations
    )
    if result is not None:
        return greenwich_full_date_from_julian_date(result[0])

    return None


def perigee_coordinates(
    epoch: Epoch,
    orbit: OrbitalElements,
    mu: GravitationalParameter = EARTH_MU,
) -> GeographicCoordinates:
    """
    Calculate the geographic coordinates of the perigee of a satellite's orbit.
    """
    time_to_perigee = time_to_true_anomaly(
        orbit,
        periapsis_true_anomaly(),
    )

    return geographic_coordinates_from_itrf(
        itrf_position_from_gcrf_position(
            epoch_offset(epoch, time_to_perigee),
            position_vector_at_time(orbit, time_to_perigee, mu),
        )
    )


def apogee_coordinates(
    epoch: Epoch,
    orbit: OrbitalElements,
    mu: GravitationalParameter = EARTH_MU,
) -> GeographicCoordinates:
    """
    Calculate the geographic coordinates of the apogee of a satellite's orbit.
    """

    time_to_apogee = time_to_true_anomaly(
        orbit,
        apoapsis_true_anomaly(),
    )

    return geographic_coordinates_from_itrf(
        itrf_position_from_gcrf_position(
            epoch_offset(epoch, time_to_apogee),
            position_vector_at_time(orbit, time_to_apogee, mu),
        )
    )
