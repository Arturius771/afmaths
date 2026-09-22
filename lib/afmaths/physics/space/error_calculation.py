import datetime

from astronomy_types import Coordinate3D

from afmaths.geometry.geometry import euclidian_distance_3d
from afmaths.physics.space.astronomy.time_functions import (
    julian_date_now,
)
from afmaths.physics.space.celestial_mechanics.state_vector import state_vector_at_time
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from afmaths.physics.space.perturbation_models.sgp4 import (
    julian_date_from_jday,
    sgp4_satrec,
    state_vector_from_satrec,
)
from afmaths.physics.space.type_conversion_helpers import (
    coordinate3d_from_vector,
    fulldate_from_python_datetime,
)


def calculate_orbital_error(
    predicted_position: Coordinate3D, actual_position: Coordinate3D
):
    """
    Calculate the error between the predicted and actual positions of a celestial body.

    Parameters:
    predicted_position (Coordinate3D): The predicted (x, y, z) position of the celestial body.
    actual_position (Coordinate3D): The actual (x, y, z) position of the celestial body.

    Returns:
    float: The Euclidean distance between the predicted and actual positions.
    """
    return euclidian_distance_3d(predicted_position, actual_position)


def orbital_error_norad_id(norad_id: int) -> float:
    """
    Placeholder function to calculate the orbital error for a satellite given its NORAD ID.

    Parameters:
    norad_id (int): The NORAD ID of the satellite.

    Returns:
    float: The orbital error for the satellite.
    """
    tle = get_tle_from_norad_id(norad_id)

    local_implementation = coordinate3d_from_vector(
        state_vector_at_time(orbital_elements_from_tle(tle)).position
    )
    sgp4_implementation = coordinate3d_from_vector(
        state_vector_from_satrec(sgp4_satrec(tle)).position
    )
    print(f"Local implementation: {local_implementation}")
    print(f"SGP4 implementation: {sgp4_implementation}")
    return calculate_orbital_error(local_implementation, sgp4_implementation)


def julian_date_error():
    return (
        julian_date_from_jday(
            fulldate_from_python_datetime(datetime.datetime.now(datetime.UTC))
        )
        - julian_date_now()
    )


if __name__ == "__main__":
    # TODO add as a test
    error = orbital_error_norad_id(25544)
    print(f"Orbital error for NORAD ID 25544: {error}")

    print(f"Julian date error: {julian_date_error()}")
